import { DEFAULT_WORKSPACE_SLUG } from "../support/constants"

const testTableColumnValue = (column, callback) => {
  cy.getByTestId("ColumnDefinitionTable").contains(column).parent().parent("tr").within(() => {
    callback()
  })
}

describe("table_columns.spec.js", () => {
  const datastore = {
    name: 'Postgres',
    slug: 'metamapper',
  }

  const table = {
    schema: 'app',
    name: 'customers',
  }

  const permissions = ["member", "readonly"]
  const databaseUri = `/${DEFAULT_WORKSPACE_SLUG}/datastores/${datastore.slug}`
  const columnsUri = `${databaseUri}/definition/${table.schema}/${table.name}/columns`

  // Tests for the basic UI components of this page.
  describe("UI", () => {
    permissions.forEach(permission => {
      describe(`as ${permission}`, () => {
        before(() => {
          cy.quickLogin(permission).then(() => cy.visit(columnsUri))
        })

        it("has the correct meta title", () => {
          cy.title().should("eq", `Columns - ${table.schema}.${table.name} - ${datastore.slug} - Metamapper`)
        })

        it("renders the columns table", () => {
          cy.getByTestId("ColumnDefinitionTable").should("exist").find("tbody").find("tr").should("have.length", 13)
        })

        it("renders the correct data types", () => {
          const testDataType = (column, type) => {
            testTableColumnValue(column, () => cy.get("td").eq(3).contains(type))
          }

          testDataType("customernumber", "integer(32)")
          testDataType("phone", "character varying(50)")
          testDataType("postalcode", "character varying(15)")
          testDataType("creditlimit", "numeric(10, 2)")
        })

        it("renders default values", () => {
          const testDefaultValue = (column, type) => {
            testTableColumnValue(column, () => cy.get("td").eq(5).contains(type))
          }

          testDefaultValue("state", "NULL::character varying")
          testDefaultValue("postalcode", "NULL::character varying")
          testDefaultValue("creditlimit", "NULL::numeric")
        })

        it("renders the primary key icon", () => {
          testTableColumnValue("customernumber", () => {
            cy.get("td").eq(1).find("i").should("be.visible").should("have.class", "anticon-key")
          })
        })

        it("renders nullable indicator", () => {
          testTableColumnValue("customernumber", () => {
            cy.get("td").eq(4).find("i").should("be.visible").should("have.class", "anticon-check-circle")
          })

          testTableColumnValue("state", () => {
            cy.get("td").eq(4).find("i").should("be.visible").should("have.class", "anticon-close-circle")
          })
        })
      })
    })
  })

  describe("update column description", () => {
    const descIndex = 6

    describe("as member", () => {
      beforeEach(() => {
        cy.quickLogin("member").then(() => cy.visit(columnsUri))
      })

      it("with valid input", () => {
        const input = "Unique ID for a customer"

        testTableColumnValue("customernumber", () => {
          cy.get("td").eq(descIndex).click().then(() => {
            cy.getByTestId("EditableCell.Input").should("be.visible")
            cy.fillInputs({"EditableCell.Input": input})
          })

          cy.get("td").eq(5).click()
          cy.get("td").eq(descIndex).contains(input)
        })

        cy.contains(".ant-message-success", "Description was saved.").should(
          "be.visible"
        )

        // Should persist after reload.
        cy.reload().then(() =>
          testTableColumnValue("customernumber", () => cy.get("td").eq(descIndex).contains(input)))
      })

      it("can reset input to nothing", () => {
        testTableColumnValue("customernumber", () => {
          cy.get("td").eq(descIndex).click().then(() => {
            cy.getByTestId("EditableCell.Input").should("be.visible")
            cy.getByTestId("EditableCell.Input").clear()
          })

          cy.get("td").eq(5).click()
          cy.get("td").eq(descIndex).find(".editable-cell-value-wrap").should("have.value", "")
        })

        cy.contains(".ant-message-success", "Description was saved.").should(
          "be.visible"
        )

        // Should persist after reload.
        cy.reload().then(() =>
          testTableColumnValue("customernumber", () => cy.get("td").eq(descIndex).should("have.value", "")))
      })

      it("with invalid input", () => {
        testTableColumnValue("phone", () => {
          const input = "This is the office phone number of the customer, which is too long of a description"

          cy.get("td").eq(descIndex).click().then(() => {
            cy.getByTestId("EditableCell.Input").should("be.visible")
            cy.fillInputs({"EditableCell.Input": input})
          })

          cy.get("td").eq(5).click()
          cy.get("td").eq(descIndex).find(".editable-cell-value-wrap").should("have.value", "")
        })

        cy.contains(".ant-message-error", "Column description cannot be longer than 50 characters.").should(
          "be.visible"
        )

        // Should persist after reload.
        cy.reload().then(() =>
          testTableColumnValue("phone", () => cy.get("td").eq(descIndex).should("have.value", "")))
      })
    })

    describe("as readonly", () => {
      beforeEach(() => {
        cy.quickLogin("readonly").then(() => cy.visit(columnsUri))
      })

      it("cannot edit the description", () => {
        testTableColumnValue("customernumber", () => {
          cy.get("td").eq(descIndex).click()
          cy.getByTestId("EditableCell.Input").should("not.be.visible")
        })
      })
    })
  })

  describe("404", () => {
    it("when workspace does not exist", () => {
      cy.quickLogin("owner")
        .then(() =>
          cy.visit("/does-not-exist/datastores/show-me/definition/potato/salad/columns"))

      cy.contains("Sorry, the page you are looking for doesn't exist.").should("be.visible")
    })

    it("when datastore does not exist", () => {
      cy.quickLogin("owner")
        .then(() =>
          cy.visit(`/${DEFAULT_WORKSPACE_SLUG}/datastores/show-me/definition/potato/salad/columns`))

      cy.contains("Sorry, the page you are looking for doesn't exist.").should("be.visible")
    })

    it("when table definition does not exist", () => {
      cy.quickLogin("owner")
        .then(() =>
          cy.visit(`/${DEFAULT_WORKSPACE_SLUG}/datastores/${datastore.slug}/definition/potato/salad/columns`))

      cy.contains("Sorry, the page you are looking for doesn't exist.").should("be.visible")
    })
  })
})
