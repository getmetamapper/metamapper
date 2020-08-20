
describe("table_overview.spec.js", () => {
  const workspace = {
    id: "d6acb06747514d17b74f21e7b00c95a4",
    slug: "gcc",
  }

  const owner = {
    email: "owner.definitions@metamapper.test",
    password: "password1234",
  }

  const member = {
    email: "member.definitions@metamapper.test",
    password: "password1234",
  }

  const readonly = {
    email: "readonly.definitions@metamapper.test",
    password: "password1234",
  }

  const outsider = {
    email: "outsider.definitions@metamapper.test",
    password: "password1234",
  }

  const datastore = {
    name: "Metamapper",
    slug: "metamapper",
  }

  const table = {
    schema: "public",
    name: "definitions_table",
  }

  const databaseUri = `/${workspace.slug}/datastores/${datastore.slug}`
  const overviewUri = `${databaseUri}/definition/${table.schema}/${table.name}/overview`

  // Tests for the basic UI components of this page.
  describe("overview", () => {
    beforeEach(() => {
      cy.login(member.email, member.password, workspace.id)
        .then(() =>
          cy.visit(overviewUri))
    })

    it("has the correct meta title", () => {
      cy.title().should("eq", `Overview - ${table.schema}.${table.name} - ${datastore.slug} - Metamapper`)
    })

    it("has the proper navigation links", () => {
      const pages = ["Overview", "Columns", "Indexes", "History"]

      pages.forEach(page => {
        cy.getByTestId(`DefinitionLayout.${page}`).should("be.visible")
      })

      cy.getByTestId("DefinitionLayout.Overview").should("have.class", "ant-menu-item-selected")
    })

    it("contains the schema and table as a title", () => {
      cy.contains(`${table.schema}.${table.name}`).should("be.visible")
    })

    it("can filter schemas and tables", () => {
      cy.get(".table-schema-selector").find(".tablename").should("have.length", 0)

      cy.getByTestId("TableSchemaSearch.Input")
        .should("be.visible")
        .type("sso")

      cy.get(".table-schema-selector").find(".tablename").should("have.length", 3)
    })
  })

  // Tests for inline editing of the table short description.
  describe("update description", () => {

    // Tests for when the logged in user is of MEMBER status.
    describe("as member", () => {
      beforeEach(() => {
        cy.login(member.email, member.password, workspace.id)
          .then(() =>
            cy.visit(overviewUri))

        cy.getByTestId("TableDescription.Container").click()
      })

      it("cannot be greater than 140 characters", () => {
        let invalidInput = "Lorem ipsum dolor sit amet, consectetuer adipiscing elit. " +
                           "Aenean commodo ligula eget dolor. Aenean massa. Cum sociis" +
                           " natoque penatibus et magnis."

        cy.fillInputs({
          "TableDescription.Input": invalidInput,
        })

        cy.getByTestId("TableDescription.Submit").should("be.visible")
        cy.getByTestId("TableDescription.Submit").click()

        cy.contains(".ant-message-error", "Table description cannot be longer than 140 characters.").should(
          "be.visible"
        )

        cy.getByTestId("TableDescription").contains("Click here to enter a brief description.")
      })

      it("can be set to something", () => {
        let validInput = "Here's a fun fact about this table."

        cy.fillInputs({
          "TableDescription.Input": validInput,
        })

        cy.getByTestId("TableDescription.Submit").should("be.visible")
        cy.getByTestId("TableDescription.Submit").click()

        cy.contains(".ant-message-success", "Description was saved.").should(
          "be.visible"
        )

        cy.reload()

        cy.getByTestId("TableDescription").contains(validInput)
      })

      it("can be set to nothing", () => {
        cy.getByTestId("TableDescription.Input").clear()

        cy.getByTestId("TableDescription.Submit").should("be.visible")
        cy.getByTestId("TableDescription.Submit").click()

        cy.contains(".ant-message-success", "Description was saved.").should(
          "be.visible"
        )

        cy.reload()

        cy.getByTestId("TableDescription").contains("Click here to enter a brief description.")
      })
    })

    // Tests for when the logged in user is of READONLY status.
    describe("as readonly", () => {
      beforeEach(() => {
        cy.login(readonly.email, readonly.password, workspace.id)
            .then(() =>
              cy.visit(overviewUri))

        cy.getByTestId("TableDescription.Container").click()
      })

      it("is disabled", () => {
        // None of the EditableText components should be visible.
        cy.getByTestId("TableDescription.Submit").should("not.be.visible")
        cy.getByTestId("TableDescription.Input").should("not.be.visible")
      })
    })
  })

  // Tests for inline editing of the table tags.
  describe("update tags", () => {
    // Tests for when the logged in user is of MEMBER status.
    describe("as member", () => {
      beforeEach(() => {
        cy.login(member.email, member.password, workspace.id)
            .then(() =>
              cy.visit(overviewUri))
      })

      it("can add tags", () => {
        const tags = [
          "warehouse",
          "dataeng",
          "analytics",
        ]

        // Make the tags input visible...
        cy.getByTestId("TableDefinitionTags.Add").click()

        // Enter the tags into the input...
        cy.getByTestId("TableDefinitionTags.Input").should("be.visible")
        cy.getByTestId("TableDefinitionTags.Input").type(tags.join('{enter}') + '{enter}')

        // Submit the updated tags...
        cy.getByTestId("TableDefinitionTags.Submit").click()

        // It displays the proper success message...
        cy.contains(".ant-message-success", "Tags were updated.").should(
          "be.visible"
        )

        cy.reload()

        tags.forEach(tag => {
          cy.get(`.ant-tag[data-test="TableDefinitionTags.Tag(${tag})"]`).should("be.visible").contains(tag)
        })
      })

      it("can remove tags", () => {
        const tag = "warehouse"

        // Open the tag input...
        cy.getByTestId("TableDefinitionTags.Add").click()

        // Remove the target tag...
        cy.get(`li[title="${tag}"]`).find(".anticon-close").click()

        // Submit the updated tags...
        cy.getByTestId("TableDefinitionTags.Submit").click()

        cy.reload().then(() =>
          cy.get(`.ant-tag[data-test="${tag}"]`).should("be.not.visible"))
      })
    })

    // Tests for when the logged in user is of READONLY status.
    describe("as readonly", () => {
      beforeEach(() => {
        cy.login(readonly.email, readonly.password, workspace.id)
            .then(() =>
              cy.visit(overviewUri))
      })

      it("is disabled", () => {
        cy.getByTestId("TableDefinitionTags.Add")
          .should("not.be.visible")

        cy.contains("Add a tag").should("not.be.visible")
      })
    })
  })

  describe("404", () => {
    it("when table definition does not exist", () => {
        cy.login(readonly.email, readonly.password, workspace.id)
          .then(() =>
            cy.visit(`${databaseUri}/definition/public/invoice_items/overview`))

      cy.contains(
        "Sorry, the page you are looking for doesn't exist."
      ).should(
        "be.visible"
      )
    })

    it("when user is unauthorized", () => {
      cy.login(outsider.email, outsider.password, workspace.id)
          .then(() =>
            cy.visit(overviewUri))

      cy.contains(
        "Sorry, the page you are looking for doesn't exist."
      ).should(
        "be.visible"
      )
    })

    it("when workspace does not exist", () => {
      cy.login(owner.email, owner.password, workspace.id)
        .then(() =>
          cy.visit("/does-not-exist/datastores/show-me/definition/potato/salad/overview"))

      cy.contains("Sorry, the page you are looking for doesn't exist.").should("be.visible")
    })

    it("when datastore does not exist", () => {
      cy.login(owner.email, owner.password, workspace.id)
        .then(() =>
          cy.visit(`/${workspace.slug}/datastores/show-me/definition/potato/salad/overview`))

      cy.contains("Sorry, the page you are looking for doesn't exist.").should("be.visible")
    })

    it("when table definition does not exist", () => {
      cy.login(owner.email, owner.password, workspace.id)
        .then(() =>
          cy.visit(`/${workspace.slug}/datastores/${datastore.slug}/definition/potato/salad/overview`))

      cy.contains("Sorry, the page you are looking for doesn't exist.").should("be.visible")
    })
  })
})
