import { DEFAULT_WORKSPACE_SLUG } from "../support/constants"

describe("datastore_overview.spec.js", () => {
  const datastore = {
    name: 'Postgres',
    slug: 'metamapper',
  }

  const databaseUri = `/${DEFAULT_WORKSPACE_SLUG}/datastores/${datastore.slug}`

  const existingProperties = [
    {
      pk: 'ow5W0kw0CK0i',
      label: 'Ownership',
      value: 'Analytics',
    },
    {
      pk: 'iPOhV1HazLW6',
      label: 'Purpose',
      value: 'Business Intelligence',
    },
  ]

  // Tests for the basic UI components of this page.
  describe("overview", () => {
    describe("as member", () => {
      beforeEach(() => {
        cy.quickLogin("member").then(() => cy.visit(databaseUri))
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
        cy.quickLogin("readonly").then(() => cy.visit(databaseUri))
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
    let allowedPermissions = ["member", "owner"]

    allowedPermissions.forEach(permission => {
      describe(`as ${permission}`, () => {
        beforeEach(() => {
          cy.quickLogin(permission)
            .then(() => cy.visit(databaseUri).wait(1000))
            .then(() => cy.getByTestId("CustomProperties.Edit").click())
        })

        it("change text field to something", () => {
          const input = "Metadata Management"

          cy.getByTestId("CustomProperties.Input(iPOhV1HazLW6)")
            .should("be.visible")
            .clear()
            .type(input)

          cy.getByTestId("CustomProperties.Submit").click()

          cy.contains(".ant-message-success", "Properties have been updated.").should(
            "be.visible"
          )

          cy.getByTestId("CustomProperties.Display(iPOhV1HazLW6)")
            .should("be.visible")
            .contains(input)
        })

        it("change text field to nothing", () => {
          cy.getByTestId(`CustomProperties.Input(iPOhV1HazLW6)`)
            .should("be.visible")
            .clear()

          cy.getByTestId("CustomProperties.Submit").click()

          cy.contains(".ant-message-success", "Properties have been updated.").should(
            "be.visible"
          )

          cy.getByTestId("CustomProperties.Display(iPOhV1HazLW6)")
            .should("have.value", "")
        })

        it("change multiple fields", () => {
          cy.fillInputs({
            "CustomProperties.Input(iPOhV1HazLW6)": "Data Warehouse",
            "CustomProperties.Input(ow5W0kw0CK0i)": "Engineering",
          })

          cy.getByTestId("CustomProperties.Submit").click()

          cy.contains(".ant-message-success", "Properties have been updated.").should(
            "be.visible"
          )

          cy.getByTestId("CustomProperties.Display(iPOhV1HazLW6)")
            .should("be.visible")
            .contains("Data Warehouse")

          cy.getByTestId("CustomProperties.Display(ow5W0kw0CK0i)")
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
