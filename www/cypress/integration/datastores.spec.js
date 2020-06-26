
describe("datastores.spec.js", () => {
  const newDatastore = {
    name: 'Metamapper Test',
    slug: 'metamapper-test',
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
      cy.getByTestId("DatastoreList").should("exist")
    })
  })

  describe("create datastore", () => {
    it("fails with readonly permission", () => {
      cy.login(readonly.email, readonly.password, workspace.id)
        .then(() =>
          cy.visit(inventoryUri))

      cy.contains("New Datastore").click()
      cy.getByTestId("DatastoreSetupForm.ValidateEngine").should("be.disabled")
    })

    it("fails when missing fields", () => {
      cy.login(owner.email, owner.password, workspace.id)
        .then(() =>
          cy.visit(inventoryUri))

      cy.contains("New Datastore").click()
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

    it("fails when cannot connect", () => {
      cy.login(member.email, member.password, workspace.id)
        .then(() =>
          cy.visit(inventoryUri))

      cy.contains("New Datastore").click()
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

    it("using UI", () => {
      cy.login(owner.email, owner.password, workspace.id)
        .then(() =>
          cy.visit(inventoryUri))

      cy.contains("New Datastore").click()

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

      // Confirm that the application redirected to the new datastore.
      cy.title().should("eq", `Datastore Overview - ${newDatastore.slug} - Metamapper`)

      cy.location("pathname").should("equal", datastoreUri)
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

      cy.wait(7500).then(() => cy.reload())

      cy.getByTestId("RunHistoryTable").get("tr").within(() => {
        cy.get("td").eq(0).contains("SUCCESS").should("be.visible")
      })
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

        cy.getByTestId("EditableCell.Input").type("This is a description")

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
          cy.get("td").eq(3).contains("This is a description")
        })

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

      cy.location("pathname").should("equal", `/${workspace.slug}/datastores`)

      cy.get(".ant-message-notice").should("be.visible")
      cy.contains(".ant-message-success", "Datastore has been removed.").should(
        "be.visible"
      )

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
