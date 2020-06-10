import { DEFAULT_WORKSPACE_SLUG } from "../support/constants"

describe("table_indexes.spec.js", () => {
  const datastore = {
    name: 'Postgres',
    slug: 'metamapper',
  }

  const databaseUri = `/${DEFAULT_WORKSPACE_SLUG}/datastores/${datastore.slug}`

  describe("UI", () => {
    describe("with single-column index", () => {
      const singleTable = {
        schema: 'app',
        name: 'departments',
      }

      const singleUri = `${databaseUri}/definition/${singleTable.schema}/${singleTable.name}/indexes`

      before(() => {
        cy.quickLogin("member").then(() => cy.visit(singleUri))
      })

      it("has the correct meta title", () => {
        cy.title().should("eq", `Indexes - ${singleTable.schema}.${singleTable.name} - ${datastore.slug} - Metamapper`)
      })

      it("contains expected indexes", () => {
        cy.getByTestId("IndexDefinitionTable").should("exist")

        cy.getByTestId("IndexDefinitionTable").contains("departments_dept_name_key").parent("tr").within(() => {
          cy.get("td").eq(0).contains("departments_dept_name_key")
          cy.get("td").eq(1).find("i").should("be.visible").should("have.class", "anticon-close-circle")
          cy.get("td").eq(2).find("i").should("be.visible").should("have.class", "anticon-check-circle")
          cy.get("td").eq(3).contains("dept_name").and("have.class", "ant-tag")
        })

        cy.getByTestId("IndexDefinitionTable").contains("departments_pkey").parent("tr").within(() => {
          cy.get("td").eq(0).contains("departments_pkey")
          cy.get("td").eq(1).find("i").should("be.visible").should("have.class", "anticon-check-circle")
          cy.get("td").eq(2).find("i").should("be.visible").should("have.class", "anticon-check-circle")
          cy.get("td").eq(3).contains("id").and("have.class", "ant-tag")
        })
      })
    })

    describe("with multi-column index", () => {
      const multipleTable = {
        schema: 'employees',
        name: 'dept_emp',
      }

      const multipleUri = `${databaseUri}/definition/${multipleTable.schema}/${multipleTable.name}/indexes`

      before(() => {
        cy.quickLogin("member").then(() => cy.visit(multipleUri))
      })

      it("has the correct meta title", () => {
        cy.title().should("eq", `Indexes - ${multipleTable.schema}.${multipleTable.name} - ${datastore.slug} - Metamapper`)
      })

      it("contains expected indexes", () => {
        cy.getByTestId("IndexDefinitionTable").should("exist")

        cy.getByTestId("IndexDefinitionTable").contains("dept_emp_pkey").parent("tr").within(() => {
          cy.get("td").eq(0).contains("dept_emp_pkey")
          cy.get("td").eq(1).find("i").should("be.visible").should("have.class", "anticon-check-circle")
          cy.get("td").eq(2).find("i").should("be.visible").should("have.class", "anticon-check-circle")
          cy.get("td").eq(3).contains("dept_no").and("have.class", "ant-tag")
          cy.get("td").eq(3).contains("emp_no").and("have.class", "ant-tag")
        })
      })
    })
  })

  describe("404", () => {
    it("when workspace does not exist", () => {
      cy.quickLogin("owner")
        .then(() =>
          cy.visit("/does-not-exist/datastores/show-me/definition/potato/salad/indexes"))

      cy.contains("Sorry, the page you are looking for doesn't exist.").should("be.visible")
    })

    it("when datastore does not exist", () => {
      cy.quickLogin("owner")
        .then(() =>
          cy.visit(`/${DEFAULT_WORKSPACE_SLUG}/datastores/show-me/definition/potato/salad/indexes`))

      cy.contains("Sorry, the page you are looking for doesn't exist.").should("be.visible")
    })

    it("when table definition does not exist", () => {
      cy.quickLogin("owner")
        .then(() =>
          cy.visit(`/${DEFAULT_WORKSPACE_SLUG}/datastores/${datastore.slug}/definition/potato/salad/indexes`))

      cy.contains("Sorry, the page you are looking for doesn't exist.").should("be.visible")
    })
  })
})
