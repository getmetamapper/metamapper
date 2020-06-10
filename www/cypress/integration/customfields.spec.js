import { DEFAULT_WORKSPACE_ID, DEFAULT_WORKSPACE_SLUG } from "../support/constants"

describe("customfields.spec.js", () => {
  before(() => {
    cy.resetdb()
  })

  let kinds = ["Datastore", "Table"]

  describe("list of custom fields", () => {
    beforeEach(() => {
      cy.login("owner@metamapper.io", "password1234", DEFAULT_WORKSPACE_ID)
        .then(() =>
          cy.visit(`/${DEFAULT_WORKSPACE_SLUG}/settings/customfields`).wait(1000))
    })

    it("displays the right meta title", () => {
      cy.title().should("eq", `Custom Fields - ${DEFAULT_WORKSPACE_SLUG} - Metamapper`)
    })

    it("displays Datastore custom fields", () => {
      cy.getByTestId("CustomFieldsTable").should("exist")

      cy.getByTestId("CustomFieldsTable").contains("Ownership").parent("tr").within(() => {
        cy.get("td").eq(0).contains("Ownership")
        cy.get("td").eq(1).contains("ENUM")
        cy.get("td").eq(2).should("be.empty")
        cy.get("td").eq(3).contains("Edit")
        cy.get("td").eq(3).contains("Delete")
      })

      cy.getByTestId("CustomFieldsTable").contains("Purpose").parent("tr").within(() => {
        cy.get("td").eq(0).contains("Purpose")
        cy.get("td").eq(1).contains("TEXT")
        cy.get("td").eq(2).contains("What this datastore is used for.")
        cy.get("td").eq(3).contains("Edit")
        cy.get("td").eq(3).contains("Delete")
      })
    })

    it("displays Table custom fields", () => {
      cy.contains("Tables").click()

      cy.getByTestId("CustomFieldsTable")
        .should("exist")
        .and("contain", "Update Cadence")
        .and("contain", "Data Steward")
        .and("contain", "Product Area")

      cy.getByTestId("CustomFieldsTable").contains("Product Area").parent("tr").within(() => {
        cy.get("td").eq(0).contains("Product Area")
        cy.get("td").eq(1).contains("ENUM")
        cy.get("td").eq(2).contains("Part of the business that table is relevant to.")
        cy.get("td").eq(3).contains("Edit")
        cy.get("td").eq(3).contains("Delete")
      })
    })
  })

  kinds.forEach(kind => {
    describe(`add custom ${kind.toLowerCase()} field`, () => {
      it(`fails with readonly permission`, () => {
        cy.login(`readonly@metamapper.io`, "password1234", DEFAULT_WORKSPACE_ID)
          .then(() =>
            cy.visit(`/${DEFAULT_WORKSPACE_SLUG}/settings/customfields`).wait(1000))

        cy.contains(kind).click()
        cy.contains(`Add Custom ${kind} Field`).should("be.disabled")

        cy.getByTestId("CustomFieldsTable").within(() => {
          cy.get("td").eq(3).should("not.have.value", "Edit")
          cy.get("td").eq(3).should("not.have.value", "Delete")
        })

        cy.logout()
      })

      describe("as owner", () => {
        beforeEach(() => {
          cy.login("owner@metamapper.io", "password1234", DEFAULT_WORKSPACE_ID)
            .then(() =>
              cy.visit(`/${DEFAULT_WORKSPACE_SLUG}/settings/customfields`).wait(1000))
        })

        describe(`create custom ${kind.toLowerCase()} field`, () => {
          it("using UI", () => {
            const formInputs = {
              name: "Cost Center",
              desc: "Where we attribute the cost of this resource.",
              type: "ENUM",
            }

            cy.contains(kind).click()
            cy.contains(`Add Custom ${kind} Field`).click()

            cy.fillInputs({
              "CustomFieldFieldset.Name": formInputs.name,
              "CustomFieldFieldset.Description": formInputs.desc,
              "CustomFieldFieldset.Type": formInputs.type,
            })

            cy.getByTestId("CustomFieldFieldset.EnumChoices").should("be.visible")
            cy.getByTestId("CustomFieldFieldset.EnumChoices").type("one{enter}two{enter}")

            // Click out of focus of the EnumChoices input.
            cy.contains(`Create New ${kind} Field`).click()

            // Submit the form.
            cy.getByTestId("CustomFieldSetupForm.Submit").click()

            cy.contains(".ant-message-success", "Custom field has been created.").should(
              "be.visible"
            )

            cy.getByTestId("CustomFieldsTable").contains(formInputs.name).parent("tr").within(() => {
              cy.get("td").eq(0).contains(formInputs.name)
              cy.get("td").eq(1).contains(formInputs.type)
              cy.get("td").eq(2).contains(formInputs.desc)
              cy.get("td").eq(3).contains("Edit")
              cy.get("td").eq(3).contains("Delete")
            })
          })

          const formValidationFixtures = [
            {
              describe: "validates field existence",
              inputs: {
                "Name": { value: "", error: "This field is required." },
                "Description": { value: "", error: null },
                "Type": { value: "ENUM", error: null },
                "EnumChoices": { value: "", error: "This field is required." },
              },
            },
            {
              describe: "validates field length",
              inputs: {
                "Name": {
                  value: (Math.random()*1e128).toString(36),
                  error: "This field must be less than 30 characters.",
                },
                "Description": {
                  value: (Math.random()*1e128).toString(36),
                  error: "This field must be less than 60 characters.",
                },
                "Type": {
                  value: "TEXT",
                  error: null,
                }
              }
            }
          ]

          formValidationFixtures.forEach(({ describe, inputs }) => {
            it(describe, () => {
              cy.contains(kind).click()
              cy.contains(`Add Custom ${kind} Field`).click()

              cy.fillInputs({
                "CustomFieldFieldset.Name": inputs["Name"]["value"],
                "CustomFieldFieldset.Description": inputs["Description"]["value"],
                "CustomFieldFieldset.Type": inputs["Type"]["value"],
              })

              cy.getByTestId("CustomFieldSetupForm.Submit").click()

              cy.verifyFormErrors("CustomFieldFieldset", inputs)
            })
          })

          it("validates field uniqueness", () => {
            const formInputs = {
              name: "Cost Center",
              desc: "",
              type: "TEXT",
            }

            cy.contains(kind).click()
            cy.contains(`Add Custom ${kind} Field`).click()

            cy.fillInputs({
              "CustomFieldFieldset.Name": formInputs.name,
              "CustomFieldFieldset.Description": formInputs.desc,
              "CustomFieldFieldset.Type": formInputs.type,
            })

            cy.getByTestId("CustomFieldSetupForm.Submit").click()

            cy.contains(".ant-message-error", "Custom field with this name already exists.").should(
              "be.visible"
            )
          })
        })

        describe(`update custom ${kind.toLowerCase()} field`, () => {
          it("cannot have a blank name", () => {
            cy.contains(kind).click()

            cy.getByTestId("CustomFieldsTable").contains("Cost Center").parent("tr").within(() => {
              cy.get("td").eq(3).contains("Edit").click()
            })

            cy.getByTestId("CustomFieldFieldset.Type").parent(".ant-select").should("have.class", "ant-select-disabled")

            cy.fillInputs({
              "CustomFieldFieldset.Name": "",
            })

            cy.getByTestId("UpdateCustomFieldForm.Submit").click()
            cy.verifyFormErrors("CustomFieldFieldset", {
              "Name": { value: "", error: "This field is required." }
            })
          })

          it("using UI", () => {
            cy.contains(kind).click()

            cy.getByTestId("CustomFieldsTable").contains("Cost Center").parent("tr").within(() => {
              cy.get("td").eq(3).contains("Edit").click()
            })

            cy.getByTestId("CustomFieldFieldset.Type").parent(".ant-select").should("have.class", "ant-select-disabled")

            cy.fillInputs({
              "CustomFieldFieldset.Description": "Something else as a description.",
            })

            cy.getByTestId("UpdateCustomFieldForm.Submit").click()
            cy.getByTestId("CustomFieldsTable").contains("Cost Center").parent("tr").within(() => {
              cy.get("td").eq(2).contains("Something else as a description.")
            })
          })
        })

        describe(`delete custom ${kind.toLowerCase()} field`, () => {
          it("using UI", () => {
            cy.contains(kind).click()

            cy.getByTestId("CustomFieldsTable").contains("Cost Center").parent("tr").within(() => {
              cy.get("td").eq(3).contains("Delete").click()
            })

            // It should open up the deletion prompt.
            cy.getByTestId("DeleteCustomField.ConfirmationPrompt").should("be.visible")
            cy.getByTestId("DeleteCustomField.Submit").should("be.visible").should("be.disabled")

            // Typing the wrong words doesn't do anything.
            cy.fillInputs({
              "DeleteCustomField.ConfirmationPrompt": "incorrect"
            })
            cy.getByTestId("DeleteCustomField.Submit").should("be.disabled")

            // Typing the right words enables the deletion prompt.
            cy.fillInputs({
              "DeleteCustomField.ConfirmationPrompt": "delete me"
            })
            cy.getByTestId("DeleteCustomField.Submit").click()

            cy.contains(".ant-message-success", "Custom field has been removed.").should(
              "be.visible"
            )

            cy.getByTestId("CustomFieldsTable").should("exist").and("contain", "Cost Center")
          })
        })
      })
    })
  })

  describe("404", () => {
    it("when workspace does not exist", () => {
      cy.login("outsider@metamapper.io", "password1234")
        .then(() =>
          cy.visit("/does-not-exist/settings/customfields"))

      cy.contains("Sorry, the page you are looking for doesn't exist.").should("be.visible")
    })

    it("when user is unauthorized", () => {
      cy.login("outsider@metamapper.io", "password1234")
        .then(() =>
          cy.visit(`/${DEFAULT_WORKSPACE_SLUG}/settings/customfields`))

      cy.contains("Sorry, the page you are looking for doesn't exist.").should("be.visible")
    })
  })
})
