import { DEFAULT_WORKSPACE_SLUG } from "../support/constants"

describe("table_properties.spec.js", () => {
  const datastore = {
    name: 'Postgres',
    slug: 'metamapper',
  }

  const table = {
    schema: 'app',
    name: 'customers',
  }

  const databaseUri = `/${DEFAULT_WORKSPACE_SLUG}/datastores/${datastore.slug}`
  const overviewUri = `${databaseUri}/definition/${table.schema}/${table.name}/overview`

  const existingProperties = [
    {
      pk: 'p0tqRz5QJ9yC',
      label: 'Product Area',
      value: 'Finance',
    },
    {
      pk: 'YjOTcEUsymIU',
      label: 'Data Steward',
      value: 'Dwight Schrute',
    },
    {
      pk: 'zI5j91vH0cfI',
      label: 'Update Cadence',
      value: '',
    }
  ]

  // Tests for the basic UI components of this page.
  describe("overview", () => {
    describe("as member", () => {
      beforeEach(() => {
        cy.quickLogin("member").then(() => cy.visit(overviewUri))
      })

      it("displays the custom properties", () => {
        existingProperties.forEach(({ pk, label, value }) => {
          cy.getByTestId(`CustomProperties.Label(${pk})`)
            .should("be.visible")
            .contains(label)

          if (value) {
            cy.getByTestId(`CustomProperties.Display(${pk})`)
              .should("be.visible")
              .contains(value)
          }
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
        cy.quickLogin("readonly").then(() => cy.visit(overviewUri))
      })

      it("displays the custom properties", () => {
        existingProperties.forEach(({ pk, label, value }) => {
          cy.getByTestId(`CustomProperties.Label(${pk})`)
            .should("be.visible")
            .contains(label)

          if (value) {
            cy.getByTestId(`CustomProperties.Display(${pk})`)
              .should("be.visible")
              .contains(value)
          }
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
            .then(() => cy.visit(overviewUri).wait(250))
            .then(() => cy.getByTestId("CustomProperties.Edit").click())
        })

        it("change user field to something else", () => {
          let input = "Dwight Schrute"

          cy.fillInputs({
            "CustomProperties.Input(YjOTcEUsymIU)": input
          })

          cy.getByTestId("CustomProperties.Submit").click()


          cy.contains(".ant-message-success", "Properties have been updated.").should(
            "be.visible"
          )

          cy.getByTestId("CustomProperties.Display(YjOTcEUsymIU)")
            .should("be.visible")
            .contains(input)
        })

        it("change user field to nothing", () => {
          cy.fillInputs({
            "CustomProperties.Input(zI5j91vH0cfI)": "(reset this property)"
          })

          cy.getByTestId("CustomProperties.Submit").click()

          cy.contains(".ant-message-success", "Properties have been updated.").should(
            "be.visible"
          )

          cy.getByTestId("CustomProperties.Display(zI5j91vH0cfI)").should("have.value", "")
        })

        it("change enum field to something else", () => {
          let input = "Daily"

          cy.fillInputs({
            "CustomProperties.Input(zI5j91vH0cfI)": input
          })

          cy.getByTestId("CustomProperties.Submit").click()

          cy.contains(".ant-message-success", "Properties have been updated.").should(
            "be.visible"
          )

          cy.getByTestId("CustomProperties.Display(zI5j91vH0cfI)")
            .should("be.visible")
            .contains(input)
        })

        it("change enum field to nothing", () => {
          cy.fillInputs({
            "CustomProperties.Input(zI5j91vH0cfI)": "(reset this property)"
          })

          cy.getByTestId("CustomProperties.Submit").click()

          cy.contains(".ant-message-success", "Properties have been updated.").should(
            "be.visible"
          )

          cy.getByTestId("CustomProperties.Display(zI5j91vH0cfI)").should("have.value", "")
        })
      })
    })
  })
})
