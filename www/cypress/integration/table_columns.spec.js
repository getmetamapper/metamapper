const testTableColumnValue = (column, callback) => {
  cy.getByTestId("ColumnDefinitionTable").contains(column).parent().parent("tr").within(() => {
    callback()
  })
}

describe("table_columns.spec.js", () => {
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

  const datastore = {
    name: "Metamapper",
    slug: "metamapper",
  }

  const table = {
    schema: "public",
    name: "revisioner_error",
  }

  const hasPermission = [
    { permission: "member", user: member },
    { permission: "owner", user: owner },
  ]

  const databaseUri = `/${workspace.slug}/datastores/${datastore.slug}`
  const columnsUri = `${databaseUri}/definition/${table.schema}/${table.name}/columns`

  // Tests for the basic UI components of this page.
  describe("UI", () => {
    hasPermission.forEach(({ permission, user }) => {
      describe(`as ${permission}`, () => {
        before(() => {
          cy.login(user.email, user.password, workspace.id).then(() => cy.visit(columnsUri))
        })

        it("has the correct meta title", () => {
          cy.title().should("eq", `Columns - ${table.schema}.${table.name} - ${datastore.slug} - Metamapper`)
        })

        it("renders the columns table", () => {
          cy.getByTestId("ColumnDefinitionTable").should("exist").find("tbody").find("tr").its("length").should("be.gte", 8)
        })

        it("renders the correct data types", () => {
          const testDataType = (column, type) => {
            testTableColumnValue(column, () => cy.get("td").eq(4).contains(type))
          }

          testDataType("id", "integer(32)")
          testDataType("exc_type", "character varying(40)")
          testDataType("exc_stacktrace", "text")
          testDataType("created_at", "timestamp with time zone")
        })

        it("renders the primary key icon", () => {
          testTableColumnValue("id", () => {
            cy.get("td").eq(2).find("i").should("be.visible").should("have.class", "anticon-key")
          })
        })

        it("renders nullable indicator", () => {
          testTableColumnValue("id", () => {
            cy.get("td").eq(5).find("i").should("be.visible").should("have.class", "anticon-close-circle")
          })

          testTableColumnValue("exc_stacktrace", () => {
            cy.get("td").eq(5).find("i").should("be.visible").should("have.class", "anticon-check-circle")
          })
        })

        it("renders expandable section", () => {
          testTableColumnValue("id", () => {
            cy.get("td").eq(0).click()
          })

          cy.contains("Comment").should("not.be.visible")

          // It should display the default value if it exists.
          cy.contains("Default Value").should("be.visible")
          cy.contains("nextval('revisioner_error_id_seq'::regclass)").should("be.visible")
        })
      })
    })
  })

  describe("update column description", () => {
    const descIndex = 6

    describe("as member", () => {
      beforeEach(() => {
        cy.login(member.email, member.password, workspace.id).then(() => cy.visit(columnsUri))
      })

      it("with valid input", () => {
        const columnName = "id"
        const input = "Unique ID for Revisioner error"

        testTableColumnValue(columnName, () => {
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
          testTableColumnValue(columnName, () => cy.get("td").eq(descIndex).contains(input)))
      })

      it("can reset input to nothing", () => {
         const columnName = "id"

        testTableColumnValue(columnName, () => {
          cy.get("td").eq(descIndex).click().then(() => {
            cy.getByTestId("EditableCell.Input").should("be.visible")
            cy.getByTestId("EditableCell.Input").clear()
          })

          cy.get("td").eq(5).click()
        })

        cy.contains(".ant-message-success", "Description was saved.").should(
          "be.visible"
        )

        testTableColumnValue(columnName, () => cy.get("td").eq(descIndex).should("have.value", ""))

        // Should persist after reload.
        cy.reload().then(() =>
          testTableColumnValue(columnName, () => cy.get("td").eq(descIndex).should("have.value", "")))
      })
    })

    describe("as readonly", () => {
      beforeEach(() => {
        cy.login(readonly.email, readonly.password, workspace.id).then(() => cy.visit(columnsUri))
      })

      it("cannot edit the description", () => {
        testTableColumnValue("id", () => {
          cy.get("td").eq(descIndex).click()

          cy.getByTestId("EditableCell.Input").should("not.be.visible")
        })
      })
    })
  })

  describe("404", () => {
    it("when workspace does not exist", () => {
      cy.login(owner.email, owner.password, workspace.id)
        .then(() =>
          cy.visit("/does-not-exist/datastores/show-me/definition/potato/salad/columns"))

      cy.contains("Sorry, the page you are looking for doesn't exist.").should("be.visible")
    })

    it("when datastore does not exist", () => {
      cy.login(owner.email, owner.password, workspace.id)
        .then(() =>
          cy.visit(`/${workspace.slug}/datastores/show-me/definition/potato/salad/columns`))

      cy.contains("Sorry, the page you are looking for doesn't exist.").should("be.visible")
    })

    it("when table definition does not exist", () => {
      cy.login(owner.email, owner.password, workspace.id)
        .then(() =>
          cy.visit(`/${workspace.slug}/datastores/${datastore.slug}/definition/potato/salad/columns`))

      cy.contains("Sorry, the page you are looking for doesn't exist.").should("be.visible")
    })
  })
})
