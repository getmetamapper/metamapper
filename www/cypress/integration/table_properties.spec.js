
describe("table_properties.spec.js", () => {
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

  const hasPermission = [
    { permission: "member", user: member },
    { permission: "owner", user: owner },
  ]

  const properties = {
    "Product Area": "RmbycHMpdVty",
    "Data Steward": "Ygh8k2mhVFvY",
    "ETL": "glsOe3AskUZ2",
  }

  const existingProperties = [
    {
      pk: properties["Product Area"],
      label: "Product Area",
      value: "Analytics",
    },
    {
      pk: properties["Data Steward"],
      label: "Data Steward",
      value: "Troy Barnes",
    },
    {
      pk: properties["ETL"],
      label: "ETL",
      value: "",
    }
  ]

  // Tests for the basic UI components of this page.
  describe("overview", () => {
    describe("as member", () => {
      beforeEach(() => {
        cy.login(member.email, member.password, workspace.id)
          .then(() =>
            cy.visit(overviewUri))
      })

      it("displays the custom properties", () => {
        existingProperties.forEach(({ pk, label, value }) => {
          if (value) {
            cy.getByTestId(`CustomProperties.Label(${pk})`)
              .should("be.visible")
              .contains(label)

            cy.getByTestId(`CustomProperties.Display(${pk})`)
              .should("be.visible")
              .contains(value)
          } else {
            cy.getByTestId(`CustomProperties.Label(${pk})`)
              .should("not.be.visible")

            cy.getByTestId(`CustomProperties.Display(${pk})`)
              .should("not.be.visible")
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
        cy.login(readonly.email, readonly.password, workspace.id)
          .then(() =>
            cy.visit(overviewUri))
      })

      it("displays the custom properties", () => {
        existingProperties.forEach(({ pk, label, value }) => {
          if (value) {
            cy.getByTestId(`CustomProperties.Label(${pk})`)
              .should("be.visible")
              .contains(label)

            cy.getByTestId(`CustomProperties.Display(${pk})`)
              .should("be.visible")
              .contains(value)
          } else {
            cy.getByTestId(`CustomProperties.Label(${pk})`)
              .should("not.be.visible")

            cy.getByTestId(`CustomProperties.Display(${pk})`)
              .should("not.be.visible")
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
    hasPermission.forEach(({ permission, user }) => {
      describe(`as ${permission}`, () => {
        beforeEach(() => {
          cy.login(user.email, user.password, workspace.id)
            .then(() => cy.visit(overviewUri).wait(250))
            .then(() => cy.getByTestId("CustomProperties.Edit").click())
        })

        it("change user field to something else", () => {
          let input = "Jeff Winger"

          cy.fillInputs({
            "CustomProperties.Input(Ygh8k2mhVFvY)": input
          })

          cy.getByTestId("CustomProperties.Submit").click()


          cy.contains(".ant-message-success", "Properties have been updated.").should(
            "be.visible"
          )

          cy.getByTestId(`CustomProperties.Display(${properties["Data Steward"]})`)
            .should("be.visible")
            .contains(input)
        })

        it("change user field to nothing", () => {
          cy.fillInputs({
            "CustomProperties.Input(Ygh8k2mhVFvY)": "(reset this property)"
          })

          cy.getByTestId("CustomProperties.Submit").click()

          cy.contains(".ant-message-success", "Properties have been updated.").should(
            "be.visible"
          )

          cy.getByTestId(`CustomProperties.Display(${properties["Data Steward"]})`)
        })

        it("change enum field to something else", () => {
          let input = "Marketing"

          cy.fillInputs({
            "CustomProperties.Input(RmbycHMpdVty)": input
          })

          cy.getByTestId("CustomProperties.Submit").click()

          cy.contains(".ant-message-success", "Properties have been updated.").should(
            "be.visible"
          )

          cy.getByTestId(`CustomProperties.Display(${properties["Product Area"]})`)
            .should("be.visible")
            .contains(input)
        })

        it("change enum field to nothing", () => {
          cy.fillInputs({
            "CustomProperties.Input(RmbycHMpdVty)": "(reset this property)"
          })

          cy.getByTestId("CustomProperties.Submit").click()

          cy.contains(".ant-message-success", "Properties have been updated.").should(
            "be.visible"
          )

          cy.getByTestId(`CustomProperties.Display(${properties["Product Area"]})`).should("have.value", "")
        })
      })
    })
  })
})
