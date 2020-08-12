
describe("table_indexes.spec.js", () => {
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

  const datastore = {
    name: "Metamapper",
    slug: "metamapper",
  }

  const databaseUri = `/${workspace.slug}/datastores/${datastore.slug}`

  describe("UI", () => {
    describe("with single-column index", () => {
      const singleTable = {
        schema: "public",
        name: "auth_workspaces",
      }

      const singleUri = `${databaseUri}/definition/${singleTable.schema}/${singleTable.name}/indexes`

      before(() => {
        cy.login(member.email, member.password, workspace.id).then(() => cy.visit(singleUri))
      })

      it("has the correct meta title", () => {
        cy.title().should("eq", `Indexes - ${singleTable.schema}.${singleTable.name} - ${datastore.slug} - Metamapper`)
      })

      it("contains expected indexes", () => {
        cy.getByTestId("IndexDefinitionTable").should("exist")

        const primaryKeyIndex = {
          name: "auth_workspaces_pkey",
          column: "id",
        }

        const secondaryIndex = {
          name: "auth_workspaces_slug_key",
          column: "slug",
        }

        cy.getByTestId("IndexDefinitionTable").contains(primaryKeyIndex.name).parent("tr").within(() => {
          cy.get("td").eq(0).contains(primaryKeyIndex.name)
          cy.get("td").eq(1).find("i").should("be.visible").should("have.class", "anticon-check-circle")
          cy.get("td").eq(2).find("i").should("be.visible").should("have.class", "anticon-check-circle")
          cy.get("td").eq(3).contains(primaryKeyIndex.column).and("have.class", "ant-tag")
        })

        cy.getByTestId("IndexDefinitionTable").contains(secondaryIndex.name).parent("tr").within(() => {
          cy.get("td").eq(0).contains(secondaryIndex.name)
          cy.get("td").eq(1).find("i").should("be.visible").should("have.class", "anticon-close-circle")
          cy.get("td").eq(2).find("i").should("be.visible").should("have.class", "anticon-check-circle")
          cy.get("td").eq(3).contains(secondaryIndex.column).and("have.class", "ant-tag")
        })
      })
    })

    describe("with multi-column index", () => {
      const multipleTable = {
        schema: "public",
        name: "auth_group_permissions",
      }

      const index = {
        name: "auth_group_permissions_group_id_permission_id_0cd325b0_uniq",
      }

      const multipleUri = `${databaseUri}/definition/${multipleTable.schema}/${multipleTable.name}/indexes`

      before(() => {
        cy.login(member.email, member.password, workspace.id).then(() => cy.visit(multipleUri))
      })

      it("has the correct meta title", () => {
        cy.title().should("eq", `Indexes - ${multipleTable.schema}.${multipleTable.name} - ${datastore.slug} - Metamapper`)
      })

      it("contains expected indexes", () => {
        cy.getByTestId("IndexDefinitionTable").should("exist")

        cy.getByTestId("IndexDefinitionTable").contains(index.name).parent("tr").within(() => {
          cy.get("td").eq(0).contains(index.name)
          cy.get("td").eq(1).find("i").should("be.visible").should("have.class", "anticon-close-circle")
          cy.get("td").eq(2).find("i").should("be.visible").should("have.class", "anticon-check-circle")
          cy.get("td").eq(3).contains("permission_id").and("have.class", "ant-tag")
          cy.get("td").eq(3).contains("group_id").and("have.class", "ant-tag")
        })
      })
    })
  })

  describe("404", () => {
    it("when workspace does not exist", () => {
      cy.login(owner.email, owner.password, workspace.id)
        .then(() =>
          cy.visit("/does-not-exist/datastores/show-me/definition/potato/salad/indexes"))

      cy.contains("Sorry, the page you are looking for doesn't exist.").should("be.visible")
    })

    it("when datastore does not exist", () => {
      cy.login(owner.email, owner.password, workspace.id)
        .then(() =>
          cy.visit(`/${workspace.slug}/datastores/show-me/definition/potato/salad/indexes`))

      cy.contains("Sorry, the page you are looking for doesn't exist.").should("be.visible")
    })

    it("when table definition does not exist", () => {
      cy.login(owner.email, owner.password, workspace.id)
        .then(() =>
          cy.visit(`/${workspace.slug}/datastores/${datastore.slug}/definition/potato/salad/indexes`))

      cy.contains("Sorry, the page you are looking for doesn't exist.").should("be.visible")
    })
  })
})
