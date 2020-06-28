
describe("datastore_overview.spec.js", () => {
  const datastore = {
    name: 'Metamapper',
    slug: 'metamapper',
  }

  const workspace = {
    id: "d6acb067-4751-4d17-b74f-21e7b00c95a4",
    slug: "gcc",
  }

  const otherWorkspace = {
    id: "acdda298-cf05-476a-9a09-d5e3ae7f02a8",
    slug: "nbc",
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

  const dataRootUri = `/${workspace.slug}/datastores`
  const databaseUri = `${dataRootUri}/${datastore.slug}`

  // Tests for inline editing of the table short description.
  describe("update description", () => {
    // Tests for when the logged in user is of MEMBER status.
    describe("as member", () => {
      beforeEach(() => {
        cy.login(member.email, member.password, workspace.id)
          .then(() =>
            cy.visit(databaseUri))

        cy.getByTestId("DatastoreDescription.Container").click()
      })

      it("cannot be greater than 140 characters", () => {
        let invalidInput = "Lorem ipsum dolor sit amet, consectetuer adipiscing elit. " +
                           "Aenean commodo ligula eget dolor. Aenean massa. Cum sociis" +
                           " natoque penatibus et magnis."

        cy.fillInputs({
          "DatastoreDescription.Input": invalidInput,
        })

        cy.getByTestId("DatastoreDescription.Submit").should("be.visible")
        cy.getByTestId("DatastoreDescription.Submit").click()

        cy.contains(
          ".ant-message-error",
          "Datastore description cannot be longer than 140 characters."
        ).should(
          "be.visible"
        )

        cy.getByTestId("DatastoreDescription").contains("Click here to enter a brief description.")
      })

      it("can be set to something", () => {
        let validInput = "Here's a fun fact about this datastore."

        cy.fillInputs({
          "DatastoreDescription.Input": validInput,
        })

        cy.getByTestId("DatastoreDescription.Submit").should("be.visible")
        cy.getByTestId("DatastoreDescription.Submit").click()

        cy.contains(".ant-message-success", "Description was saved.").should(
          "be.visible"
        )

        cy.reload().then(() => cy.getByTestId("DatastoreDescription").contains(validInput))
      })

      it("can be set to nothing", () => {
        cy.getByTestId("DatastoreDescription.Input").clear()

        cy.getByTestId("DatastoreDescription.Submit").should("be.visible")
        cy.getByTestId("DatastoreDescription.Submit").click()

        cy.contains(".ant-message-success", "Description was saved.").should(
          "be.visible"
        )

        cy.reload().then(() => cy.getByTestId("DatastoreDescription").contains("Click here to enter a brief description."))
      })
    })

    // Tests for when the logged in user is of READONLY status.
    describe("as readonly", () => {
      beforeEach(() => {
        cy.login(readonly.email, readonly.password, workspace.id)
          .then(() =>
            cy.visit(databaseUri))

        cy.getByTestId("DatastoreDescription.Container").click()
      })

      // None of the EditableText components should be visible.
      it("is disabled", () => {
        cy.getByTestId("DatastoreDescription.Submit").should("not.be.visible")
        cy.getByTestId("DatastoreDescription.Input").should("not.be.visible")
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
            cy.visit(databaseUri))
      })

      it("can add tags", () => {
        const tags = [
          "warehouse",
          "dataeng",
          "analytics",
        ]

        // Make the tags input visible...
        cy.getByTestId("DatastoreTags.Add").click()

        // Enter the tags into the input...
        cy.getByTestId("DatastoreTags.Input").should("be.visible")
        cy.getByTestId("DatastoreTags.Input").type(tags.join('{enter}') + '{enter}')

        // Submit the updated tags...
        cy.getByTestId("DatastoreTags.Submit").click()

        // It displays the proper success message...
        cy.contains(".ant-message-success", "Tags were updated.").should(
          "be.visible"
        )

        cy.reload()

        tags.forEach(tag => {
          cy.get(`.ant-tag[data-test="DatastoreTags.Tag(${tag})"]`).should("be.visible").contains(tag)
        })
      })

      it("can remove tags", () => {
        const tag = "warehouse"

        // Open the tag input...
        cy.getByTestId("DatastoreTags.Add").click()

        // Remove the target tag...
        cy.get(`li[title="${tag}"]`).find(".anticon-close").click()

        // Submit the updated tags...
        cy.getByTestId("DatastoreTags.Submit").click()

        cy.reload().then(() => cy.get(`.ant-tag[data-test="${tag}"]`).should("be.not.visible"))
      })
    })

    // Tests for when the logged in user is of READONLY status.
    describe("as readonly", () => {
      it("is disabled", () => {
        cy.login(readonly.email, readonly.password, workspace.id)
          .then(() =>
            cy.visit(databaseUri))

        cy.getByTestId("DatastoreTags.Add").should("not.be.visible")

        cy.contains("Add a tag").should("not.be.visible")
      })
    })
  })

  describe("404", () => {
    it("when datastore does not exist", () => {
      cy.login(owner.email, owner.password, workspace.id)
        .then(() =>
          cy.visit(`/${dataRootUri}/not-a-database`))

      cy.contains(
        "Sorry, the page you are looking for doesn't exist."
      ).should(
        "be.visible"
      )
    })

    it("when user is unauthorized", () => {
      cy.login(outsider.email, outsider.password, otherWorkspace.id)
        .then(() =>
          cy.visit(databaseUri))

      cy.contains(
        "Sorry, the page you are looking for doesn't exist."
      ).should(
        "be.visible"
      )
    })
  })
})
