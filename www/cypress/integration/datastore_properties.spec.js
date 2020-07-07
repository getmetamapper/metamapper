
describe("datastore_properties.spec.js", () => {
  const datastore = {
    name: 'Metamapper',
    slug: 'metamapper',
  }

  const workspace = {
    id: "d6acb067-4751-4d17-b74f-21e7b00c95a4",
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

  const hasPermission = [
    { permission: "member", user: member },
    { permission: "owner", user: owner },
  ]

  const databaseUri = `/${workspace.slug}/datastores/${datastore.slug}`

  const properties = {
    "Purpose": "J3M63WcYJkwN",
    "Ownership": "lYj8WxYvKVqj",
  }

  const existingProperties = [
    {
      pk: properties["Ownership"],
      label: "Ownership",
      value: "Engineering",
    },
    {
      pk: properties["Purpose"],
      label: "Purpose",
      value: "Business Intelligence",
    },
  ]

  // Tests for the basic UI components of this page.
  describe("overview", () => {
    describe("as member", () => {
      beforeEach(() => {
        cy.login(member.email, member.password, workspace.id)
          .then(() =>
            cy.visit(databaseUri))
      })

      it("displays the custom properties", () => {
        existingProperties.forEach(({ pk, label, value }) => {
          cy.getByTestId(`CustomProperties.Label(${pk})`).should("be.visible").contains(label)
          cy.getByTestId(`CustomProperties.Display(${pk})`).should("be.visible").contains(value)
        })
      })

      it("displays the manage custom fields button", () => {
        cy.getByTestId("CustomProperties.Manage").should("be.visible")
      })

      it("displays the edit properties button",() => {
        cy.getByTestId("CustomProperties.Edit").should("be.visible")
      })
    })

    describe("as readonly", () => {
      beforeEach(() => {
        cy.login(readonly.email, readonly.password, workspace.id)
          .then(() =>
            cy.visit(databaseUri))
      })

      it("displays the custom properties", () => {
        existingProperties.forEach(({ pk, label, value }) => {
          cy.getByTestId(`CustomProperties.Label(${pk})`).should("be.visible").contains(label)
          cy.getByTestId(`CustomProperties.Display(${pk})`).should("be.visible").contains(value)
        })
      })

      it("displays the manage custom fields button", () => {
        cy.getByTestId("CustomProperties.Manage").should("be.visible")
      })

      it("does not display the edit properties button", () => {
        cy.getByTestId("CustomProperties.Edit").should("not.be.visible")
      })
    })
  })

  describe("update properties", () => {
    hasPermission.forEach(({ permission, user }) => {
      describe(`as ${permission}`, () => {
        beforeEach(() => {
          cy.login(user.email, user.password, workspace.id)
            .then(() => cy.visit(databaseUri))
            .then(() => cy.getByTestId("CustomProperties.Edit").click())
        })

        it("change text field to something", () => {
          const input = "Metadata Management"

          cy.getByTestId(`CustomProperties.Input(${properties["Purpose"]})`)
            .should("be.visible")
            .clear()
            .type(input)

          cy.getByTestId("CustomProperties.Submit").click()

          cy.contains(".ant-message-success", "Properties have been updated.").should(
            "be.visible"
          )

          cy.getByTestId(`CustomProperties.Display(${properties["Purpose"]})`)
            .should("be.visible")
            .contains(input)
        })

        it("change text field to nothing", () => {
          cy.getByTestId(`CustomProperties.Input(${properties["Purpose"]})`)
            .should("be.visible")
            .clear()

          cy.getByTestId("CustomProperties.Submit").click()

          cy.contains(".ant-message-success", "Properties have been updated.").should(
            "be.visible"
          )

          cy.getByTestId(`CustomProperties.Display(${properties["Purpose"]})`).should("have.value", "")
        })

        it("change multiple fields", () => {
          cy.fillInputs({
            "CustomProperties.Input(J3M63WcYJkwN)": "Data Warehouse",
            "CustomProperties.Input(lYj8WxYvKVqj)": "Engineering",
          })

          cy.getByTestId("CustomProperties.Submit").click()

          cy.contains(".ant-message-success", "Properties have been updated.").should(
            "be.visible"
          )

          cy.getByTestId(`CustomProperties.Display(${properties["Purpose"]})`)
            .should("be.visible")
            .contains("Data Warehouse")

          cy.getByTestId(`CustomProperties.Display(${properties["Ownership"]})`)
            .should("be.visible")
            .contains("Engineering")
        })

        it("displays the update activity via the UI", () => {
          cy.contains(
            `updated custom properties on the ${datastore.name} datastore.`
          ).should(
            "be.visible"
          )
        })
      })
    })
  })
})
