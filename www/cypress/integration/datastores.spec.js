
describe("datastores.spec.js", () => {
  const newDatastore = {
    name: 'Metamapper Test',
    slug: 'metamapper-test',
  }

  const workspace = {
    id: "d6acb06747514d17b74f21e7b00c95a4",
    slug: "gcc",
  }

  const owner = {
    name: "Jeff Winger",
    email: "owner.definitions@metamapper.test",
    password: "password1234",
  }

  const member = {
    name: "Abed Nadir",
    email: "member.definitions@metamapper.test",
    password: "password1234",
  }

  const otherMember = {
    name: "Troy Barnes",
    email: "other.member.definitions@metamapper.test",
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

  const inventoryUri = `/${workspace.slug}/datastores/`
  const datastoreUri = `${inventoryUri}${newDatastore.slug}`

  describe("list datastores", () => {
    before(() => {
      cy.login(member.email, member.password, workspace.id)
        .then(() =>
          cy.visit(inventoryUri))
    })

    it("has the correct meta title", () => {
      cy.title().should("eq", `Datastores - ${workspace.slug} - Metamapper`)
    })

    it("displays the list of datastores", () => {
      cy.getByTestId("DatastoreList").should("exist").should("contain", "Metamapper")
    })
  })

  describe("create datastore", () => {
    it("fails with readonly permission", () => {
      cy.login(readonly.email, readonly.password, workspace.id)
        .then(() =>
          cy.visit(inventoryUri))

      cy.contains("Connect a Datastore").click()
      cy.getByTestId("DatastoreSetupForm.ValidateEngine").should("be.disabled")
    })

    it("fails when missing fields", () => {
      cy.login(member.email, member.password, workspace.id)
        .then(() =>
          cy.visit(inventoryUri))

      cy.contains("Connect a Datastore").click()
      cy.contains("PostgreSQL").click()

      cy.getByTestId("DatastoreSetupForm.ValidateEngine").click()

      cy.fillInputs({
        "ConnectionSettingsFieldset.Host": "database",
        "ConnectionSettingsFieldset.Username": "postgres",
        "ConnectionSettingsFieldset.Password": "postgres",
        "ConnectionSettingsFieldset.Database": "metamapper",
      })

      cy.getByTestId("DatastoreSetupForm.TestConnection")
        .should("be.visible")
        .should("contain", "Test Connection")
        .click()

      cy.contains(
        ".ant-message-error", "Please fill out all the required fields."
      ).should(
        "be.visible"
      )
    })

    it("fails when Postgres cannot connect", () => {
      cy.login(member.email, member.password, workspace.id)
        .then(() =>
          cy.visit(inventoryUri))

      cy.contains("Connect a Datastore").click()
      cy.contains("PostgreSQL").click()

      cy.getByTestId("DatastoreSetupForm.ValidateEngine").click()

      cy.fillInputs({
        "ConnectionSettingsFieldset.Host": "database",
        "ConnectionSettingsFieldset.Port": "-5555",
        "ConnectionSettingsFieldset.Username": "postgres",
        "ConnectionSettingsFieldset.Password": "postgres",
        "ConnectionSettingsFieldset.Database": "metamapper",
      })

      cy.getByTestId("DatastoreSetupForm.TestConnection")
        .should("be.visible")
        .should("contain", "Test Connection")
        .click()

      cy.contains(
        ".ant-message-error", "Could not connect to datastore with these credentials."
      ).should(
        "be.visible"
      )

      // Test Connection button should still be visible.
      cy.getByTestId("DatastoreSetupForm.TestConnection")
        .should("be.visible")
        .should("contain", "Test Connection")
    })

    it("fails when MySQL cannot connect", () => {
      cy.login(member.email, member.password, workspace.id)
        .then(() =>
          cy.visit(inventoryUri))

      cy.contains("Connect a Datastore").click()
      cy.contains("MySQL").click()

      cy.getByTestId("DatastoreSetupForm.ValidateEngine").click()

      cy.fillInputs({
        "ConnectionSettingsFieldset.Host": "mysqldb",
        "ConnectionSettingsFieldset.Port": "3306",
        "ConnectionSettingsFieldset.Username": "employees",
        "ConnectionSettingsFieldset.Password": "notreal",
        "ConnectionSettingsFieldset.Database": "employees",
      })

      cy.getByTestId("DatastoreSetupForm.TestConnection")
        .should("be.visible")
        .should("contain", "Test Connection")
        .click()

      cy.contains(
        ".ant-message-error", "2003: Can't connect to MySQL server on 'mysqldb:3306' (-2 Name or service not known)"
      ).should(
        "be.visible"
      )

      cy.getByTestId("DatastoreSetupForm.TestConnection")
        .should("be.visible")
        .should("contain", "Test Connection")
    })

    it("fails when Snowflake cannot connect", () => {
      cy.login(member.email, member.password, workspace.id)
        .then(() =>
          cy.visit(inventoryUri))

      cy.contains("Connect a Datastore").click()
      cy.contains("Snowflake").click()

      cy.getByTestId("DatastoreSetupForm.ValidateEngine").click()

      cy.fillInputs({
        "ConnectionSettingsFieldset.Host": "mm-testing",
        "ConnectionSettingsFieldset.Username": "cypress",
        "ConnectionSettingsFieldset.Password": "automated-cypress-test",
        "ConnectionSettingsFieldset.Database": "test_db",
      })

      cy.getByTestId("DatastoreSetupForm.TestConnection")
        .should("be.visible")
        .should("contain", "Test Connection")
        .click()

      cy.contains(
        ".ant-message-error", "250001 (08001): Failed to connect to DB. Verify the account name is correct: mm-testing.snowflakecomputing.com:443. HTTP 403: Forbidden"
      ).should(
        "be.visible"
      )

      cy.getByTestId("DatastoreSetupForm.TestConnection")
        .should("be.visible")
        .should("contain", "Test Connection")
    })

    it("using UI", () => {
      cy.login(member.email, member.password, workspace.id)
        .then(() =>
          cy.visit(inventoryUri))

      cy.contains("Connect a Datastore").click()

      // It navigates to the correct page.
      cy.location("pathname").should("equal", `/${workspace.slug}/datastores/new`)

      cy.title().should("eq", `Datastore Setup - ${workspace.slug} - Metamapper`)

      // Step 1 - Select a database engine.
      cy.contains("PostgreSQL").click()
      cy.getByTestId("DatastoreSetupForm.ValidateEngine").click()

      // Step 2 – Enter valid credentials.
      cy.fillInputs({
        "ConnectionSettingsFieldset.Host": "database",
        "ConnectionSettingsFieldset.Port": "5432",
        "ConnectionSettingsFieldset.Username": "postgres",
        "ConnectionSettingsFieldset.Password": "postgres",
        "ConnectionSettingsFieldset.Database": "metamapper",
      })

      cy.getByTestId("DatastoreSetupForm.TestConnection")
        .should("be.visible")
        .should("contain", "Test Connection")
        .click()
        .then(() => cy.wait(1500))

      cy.getByTestId("DatastoreSetupForm.TestConnection")
        .should("not.be.visible")

      cy.getByTestId("DatastoreSetupForm.VerifyConnection")
        .should("be.visible")
        .should("contain", "Continue")
        .click()

      // Step 3 – Enter metadata about the datastore.
      cy.fillInputs({
        "DatastoreSettingsFieldset.Nickname": newDatastore.name,
      })

      cy.getByTestId("DatastoreSetupForm.Submit").click()

      // Confirm that the application redirected to the Connect a Datastore.
      cy.title().should("eq", `Datastore Overview - ${newDatastore.slug} - Metamapper`)

      cy.location("pathname").should("equal", datastoreUri)
    })
  })

  describe("datastore access", () => {
    describe("as non-permitted member", () => {
      beforeEach(() => {
        cy.login(readonly.email, readonly.password, workspace.id)
          .then(() =>
            cy.visit(inventoryUri))
      })

      it("removes the datastore from the viewable list", () =>{
        cy.getByTestId("DatastoreList").should("exist").should("not.contain", newDatastore.name)
      })
    })

    describe("as owner", () => {
      beforeEach(() => {
        cy.login(owner.email, owner.password, workspace.id)
          .then(() =>
            cy.visit(datastoreUri))

        cy.contains("Access").click()
      })

      it("displays the correct meta title", () => {
        cy.title().should("eq", `Access - ${newDatastore.slug} - Metamapper`)
      })

      it("contain the user that created the datastore", () => {
        cy.getByTestId("DatastoreAccessUserPrivilegesTable").should("be.visible").should("contain", member.name)
        cy.getByTestId("DatastoreAccessUserPrivilegesTable").should("be.visible")

        cy.getByTestId("DatastoreAccessUserPrivilegesTable").contains(member.name).parent().parent("tr").within(() => {
          for (var i = 1; i <= 6; i++) {
            cy.get("td").eq(i).find("i").should("be.visible").should("have.class", "anticon-check-circle")
          }
        })
      })

      it("can disable limited access", () => {
        cy.getByTestId("ToggleDatastoreObjectPermissions").click().then(() => cy.wait(1000))
        cy.getByTestId("ToggleDatastoreObjectPermissions").should("not.have.class", "ant-switch-checked")

        cy.getByTestId("DatastoreAccessUserPrivilegesTable")
          .should("not.be.visible")

        cy.getByTestId("DatastoreAccessGroupPrivilegesTable")
          .should("not.be.visible")

        cy.reload()

        cy.location("pathname").should("equal", `${datastoreUri}/access`)

        cy.getByTestId("ToggleDatastoreObjectPermissions").should("not.have.class", "ant-switch-checked")

        cy.getByTestId("DatastoreAccessUserPrivilegesTable")
          .should("not.be.visible")

        cy.getByTestId("DatastoreAccessGroupPrivilegesTable")
          .should("not.be.visible")
      })
    })

    describe("as non-permitted member", () => {
      beforeEach(() => {
        cy.login(otherMember.email, otherMember.password, workspace.id)
          .then(() =>
            cy.visit(datastoreUri))

        cy.contains("Access").click()
      })

      it("cannot toggle limited access", () => {
        cy.getByTestId("ToggleDatastoreObjectPermissions").should("not.have.class", "ant-switch-checked")
        cy.getByTestId("ToggleDatastoreObjectPermissions").click()

        cy.getByTestId("ToggleDatastoreObjectPermissions").should("have.class", "ant-switch-checked")

        cy.contains(
          ".ant-message-error", "You do not have permission to perform this action."
        ).should(
          "be.visible"
        )
      })
    })
  })

  describe("run history", () => {
    beforeEach(() => {
      cy.login(owner.email, owner.password, workspace.id)
        .then(() =>
          cy.visit(datastoreUri))

      cy.contains("Run History").click()
    })

    it("displays the correct meta title", () => {
      cy.title().should("eq", `Run History - ${newDatastore.slug} - Metamapper`)
    })

    it("should navigate to the Run History page", () => {
      cy.location("pathname").should("equal", `${datastoreUri}/runs`)

      cy.getByTestId("RunHistoryTable").should("exist")

      cy.wait(2500).then(() => cy.reload())

      cy.getByTestId("RunHistoryTable").get("tr").within(() => {
        cy.get("td").eq(0).contains("SUCCESS").should("be.visible")
      })
    })

    it("displays the revisioner logs table", () => {
      cy.contains("change(s) detected").should("be.visible").click()

      cy.getByTestId("RunRevisionLogTable")
        .should("exist")
        .find("tbody")
        .find("tr")
        .its("length")
        .should("be.gte", 10)

      cy.getByTestId("RunRevisionLogTable")
        .should("contain", "Schema named public was created.")
        .should("contain", "Table named auth_memberships was added to the public schema.")
    })
  })

  describe("asset catalog", () => {
    describe("as member", () => {
      beforeEach(() => {
        cy.login(owner.email, owner.password, workspace.id)
          .then(() =>
            cy.visit(datastoreUri))

        cy.contains("Assets").click()
      })

      it("displays the correct meta title", () => {
        cy.title().should("eq", `Datastore Assets - ${newDatastore.slug} - Metamapper`)
      })

      it("should navigate to the Data Assets page", () => {
        cy.location("pathname").should("equal", `${datastoreUri}/assets`)

        cy.getByTestId("DatastoreAssetsTable")
          .should("exist")
          .and("contain", "audit_activity")
          .and("contain", "auth_users")
          .and("contain", "auth_workspaces")
          .and("contain", "definitions_datastore")
          .and("contain", "definitions_table")
      })

      it("can update description", () => {
        cy.getByTestId("DatastoreAssetsTable").contains("td", "audit_activity").parent("tr").within(() => {
          cy.get("td").eq(1).contains("audit_activity")
          cy.get("td").eq(2).contains("Base table")
          cy.get("td").eq(3).click()
        })

        cy.getByTestId("EditableCell.Input").clear().type("This is a description")

        cy.contains("public").first().click()
        cy.contains(".ant-message-success", "Description was saved.").should(
          "be.visible"
        )
      })
    })

    describe("as readonly", () => {
      beforeEach(() => {
        cy.login(readonly.email, readonly.password, workspace.id)
          .then(() =>
            cy.visit(datastoreUri))

        cy.contains("Assets").click()
      })

      it("cannot update description", () => {
        cy.getByTestId("DatastoreAssetsTable").contains("td", "audit_activity").parent("tr").within(() => {
          cy.get("td").eq(1).contains("audit_activity")
          cy.get("td").eq(2).contains("Base table")
          cy.get("td").eq(3).click()
        })

        cy.getByTestId("EditableCell.Input").should("not.exist")

        cy.getByTestId("DatastoreAssetsTable").contains("td", "auth_workspaces").parent("tr").within(() => {
          cy.get("td").eq(1).contains("auth_workspaces")
          cy.get("td").eq(2).contains("Base table")
          cy.get("td").eq(3).should("be.empty")
        })
      })
    })

    describe("not found", () => {
      it("when datastore does not exist", () => {
        cy.login(owner.email, owner.password, workspace.id)
          .then(() =>
            cy.visit(`/${inventoryUri}/not-a-database/assets`))

        cy.contains(
          "Sorry, the page you are looking for doesn't exist."
        ).should(
          "be.visible"
        )
      })
    })

    describe("filtering", () => {
      it("can filter by asset name", () => {
        cy.login(owner.email, owner.password, workspace.id)
          .then(() =>
            cy.visit(`/${inventoryUri}metamapper/assets`))

        cy.getByTestId("DatastoreAssetSearch.Submit").clear().type("comments{enter}")

        cy.location("pathname").should("equal", `${inventoryUri}metamapper/assets`)
        cy.location("search").should("equal", `?search=comments`)

        cy.getByTestId("DatastoreAssetsTable").should("exist").find("tbody").find("tr").its("length").should("be.equal", 1)
      })

      it("can filter by schema name", () => {
        cy.login(owner.email, owner.password, workspace.id)
          .then(() =>
            cy.visit(`/${inventoryUri}metamapper/definition/admin/access_logs/overview`))

        cy.getByTestId("DatastoreLayout.Breadcrumbs").contains("admin").click()

        cy.location("pathname").should("equal", `${inventoryUri}metamapper/assets`)
        cy.location("search").should("equal", `?schema=admin`)

        cy.getByTestId("DatastoreAssetsTable").should("exist").find("tbody").find("tr").its("length").should("be.equal", 1)

        // Test that we append search parameters...
        cy.getByTestId("DatastoreAssetSearch.Submit").clear().type("comments{enter}")

        cy.location("pathname").should("equal", `${inventoryUri}metamapper/assets`)
        cy.location("search").should("equal", `?schema=admin&search=comments`)

        cy.getByTestId("DatastoreAssetsTable").contains("No Data").should("be.visible")
      })
    })
  })

  describe("update datastore connection", () => {
    describe("as member", () => {
      beforeEach(() => {
        cy.login(member.email, member.password, workspace.id)
          .then(() =>
            cy.visit(datastoreUri))

        cy.contains("Connection").click()
      })

      it("displays the correct meta title", () => {
        cy.title().should("eq", `Connection Settings - ${newDatastore.slug} - Metamapper`)
      })

      it("can update the datastore", () => {
        cy.fillInputs({
          "ConnectionSettingsFieldset.Password": "postgres"
        })

        cy.getByTestId("ConnectionSettingsForm.Submit").click()

        cy.contains(
          ".ant-message-success", "Connection has been updated."
        ).should(
          "be.visible"
        )
      })

      it("throws error for bad connection", () => {
        cy.fillInputs({
          "ConnectionSettingsFieldset.Password": "password1234"
        })

        cy.getByTestId("ConnectionSettingsForm.Submit").click()

        cy.contains(
          ".ant-message-error", "Could not connect to datastore with these credentials."
        ).should(
          "be.visible"
        )
      })
    })

    describe("as readonly", () => {
      beforeEach(() => {
        cy.login(readonly.email, readonly.password, workspace.id)
          .then(() =>
            cy.visit(datastoreUri))

        cy.contains("Connection").click()
      })

      it("displays the correct meta title", () => {
        cy.title().should("eq", `Connection Settings - ${newDatastore.slug} - Metamapper`)
      })

      it("cannot update datastore connection", () => {
        cy.formIsDisabled("ConnectionSettingsFieldset")
      })
    })

    describe("not found", () => {
      it("when datastore does not exist", () => {
        cy.login(owner.email, owner.password, workspace.id)
          .then(() =>
            cy.visit(`/${inventoryUri}/not-a-database/connection`))

        cy.contains(
          "Sorry, the page you are looking for doesn't exist."
        ).should(
          "be.visible"
        )
      })
    })
  })

  describe("update datastore metadata", () => {
    describe("as member", () => {
      beforeEach(() => {
        cy.login(member.email, member.password, workspace.id)
          .then(() =>
            cy.visit(datastoreUri))

        cy.contains("Settings").click()
      })

      it("displays the correct meta title", () => {
        cy.title().should("eq", `Datastore Settings - ${newDatastore.slug} - Metamapper`)
      })

      it("can update datastore metadata", () => {
        cy.getByTestId("DatastoreSettingsFieldset.Enabled").click()
        cy.getByTestId("DatastoreSettingsFieldset.Tags").should("be.visible")
        cy.getByTestId("DatastoreSettingsFieldset.Tags").type("one{enter}two{enter}")

        cy.getByTestId("DatastoreSettingsForm.Submit").click()

        cy.get(".ant-message-notice").should("be.visible")
        cy.contains(".ant-message-success", "Datastore has been updated.").should(
          "be.visible"
        )
      })
    })

    describe("as readonly", () => {
      beforeEach(() => {
        cy.login(readonly.email, readonly.password, workspace.id)
          .then(() =>
            cy.visit(datastoreUri))

        cy.contains("Settings").click()
      })

      it("displays the correct meta title", () => {
        cy.title().should("eq", `Datastore Settings - ${newDatastore.slug} - Metamapper`)
      })

      it("cannot update datastore metadata", () => {
        cy.formIsDisabled("DatastoreSettingsFieldset")
      })
    })

    describe("not found", () => {
      it("when datastore does not exist", () => {
        cy.login(owner.email, owner.password, workspace.id)
          .then(() =>
            cy.visit(`/${inventoryUri}/not-a-database/settings`))

        cy.contains(
          "Sorry, the page you are looking for doesn't exist."
        ).should(
          "be.visible"
        )
      })
    })
  })

  describe("delete datastore", () => {
    it("with readonly permissions", () => {
      cy.login(readonly.email, readonly.password, workspace.id)
        .then(() =>
          cy.visit(datastoreUri))

      cy.contains("Settings").click()

      // We don't even display the link to delete the datastore.
      cy.getByTestId("DeleteDatastore.Open").should("not.be.visible")
    })

    it("with basic permissions", () => {
      cy.login(member.email, member.password, workspace.id)
        .then(() =>
          cy.visit(datastoreUri))

      cy.contains("Settings").click()

      cy.getByTestId("DeleteDatastore.Open").click()

      cy.fillInputs({
        "DeleteDatastore.ConfirmationPrompt": "delete me"
      })

      cy.getByTestId("DeleteDatastore.Submit").click()

      cy.get(".ant-message-notice").should("be.visible")
      cy.contains(".ant-message-success", "Datastore has been removed.").should(
        "be.visible"
      )

      cy.location("pathname").should("equal", `/${workspace.slug}/datastores`)

      cy.getByTestId("DatastoreList").should("exist").and("not.contain", newDatastore.name)
    })
  })

  describe("404", () => {
    it("when workspace does not exist", () => {
      cy.login(owner.email, owner.password, workspace.id)
        .then(() =>
          cy.visit("/does-not-exist/datastores"))

      cy.contains("Sorry, the page you are looking for doesn't exist.").should("be.visible")
    })

    it("when user is unauthorized", () => {
      cy.login(outsider.email, outsider.password)
        .then(() =>
          cy.visit(`/${workspace.slug}/datastores`))

      cy.contains("Sorry, the page you are looking for doesn't exist.").should("be.visible")
    })
  })
})
