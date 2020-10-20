describe("table_column_readme.spec.js", () => {
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

  const databaseUri = `/${workspace.slug}/datastores/${datastore.slug}`

  describe("overview", () => {
    const overviewUri = `${databaseUri}/definition/public/definitions_table/columns?selectedColumn=Q29sdW1uVHlwZTo1MDE=`

    describe("when README exists", () => {
      describe("write access", () => {
        before(() => {
          cy.login(owner.email, owner.password, workspace.id).then(() => cy.visit(overviewUri))
        })

        it("displays the README text", () => {
          cy.getByTestId("ColumnReadme").contains("The type of entity that this row represents.")
          cy.getByTestId("ColumnReadme").get("h3").contains("The \"kind\" column")
        })

        it("has edit prompt", () => {
          cy.getByTestId("ColumnReadme").should("be.visible")
          cy.getByTestId("ColumnReadme.Edit").should("be.visible")
          cy.getByTestId("ColumnReadme").contains("You can click here to edit this README.")
        })
      })

      describe("read access", () => {
        before(() => {
          cy.login(readonly.email, readonly.password, workspace.id).then(() => cy.visit(overviewUri))
        })

        it("does not have edit prompt", () => {
          cy.getByTestId("ColumnReadme").should("be.visible")
          cy.getByTestId("ColumnReadme.Edit").should("not.be.visible")
        })
      })
    })
  })

  describe("editor", () => {
    const overviewUri = `${databaseUri}/definition/public/definitions_table/columns?selectedColumn=Q29sdW1uVHlwZTo1MTc=`

    describe("editing the README", () => {
      describe("write access", () => {
        it("shows the edit button", () => {
          cy.login(owner.email, owner.password, workspace.id)
            .then(() => cy.visit(overviewUri))

          cy.getByTestId("ColumnReadme").should("be.visible")
          cy.getByTestId("ColumnReadme.Edit").should("be.visible")
          cy.getByTestId("ColumnReadme.Edit").click()

          cy.location("pathname")
            .should(
              "equal",
              `${databaseUri}/definition/public/definitions_table/columns/name/readme/edit`
            )

          cy.getByTestId("ReadmeMirrorEditor.Editor").should("be.visible")
        })

        beforeEach(() => {
          cy.login(owner.email, owner.password, workspace.id)
            .then(() => cy.visit(`${databaseUri}/definition/public/definitions_table/columns/name/readme/edit`))
        })

        it("prompts when unsaved", () => {
          const stub = cy.stub()

          cy.on('window:confirm', stub)

          cy.getByTestId("ReadmeMirrorEditor.Editor").should("be.visible")
          cy.getByTestId("ReadmeMirrorEditor.Editor")
            .click()
            .type("{enter}{enter}This should not be saved.")

          cy.getByTestId("ReadmeMirrorEditor.Close").click()
            .then(() => {
              expect(stub.getCall(0)).to.be.calledWith('You have unsaved changes. Are you sure you want to leave?')
            })
        })

        it("updates the README", () => {
          cy.getByTestId("ReadmeMirrorEditor.Editor").should("be.visible")
          cy.getByTestId("Readme").should("be.visible")

          cy.getByTestId("ReadmeMirrorEditor.Editor")
            .click()
            .type("{enter}{enter}# Welcome")
            .type("{enter}{enter}This is a test")
            .type("{enter}{enter}## Code")
            .type("{enter}{enter}```javascript{enter}var x = 1 + 1{enter}```")
            .type("{enter}{enter}Pretty cool.")


          // It should save the README.
          cy.getByTestId("ReadmeMirrorEditor.Submit").click()
          cy.contains(".ant-message-success", "Changes have been saved.").should(
            "be.visible"
          )

          // It renders input as Markdown
          cy.getByTestId("Readme").get("h1").contains("Welcome")
          cy.getByTestId("Readme").get("h2").contains("Code")
          cy.getByTestId("Readme").get("pre").contains("var x = 1 + 1")
          cy.getByTestId("Readme").get("p").contains("This is a test")
          cy.getByTestId("Readme").get("p").contains("Pretty cool.")

          // It should close to the base path.
          cy.getByTestId("ReadmeMirrorEditor.Close").click()
          cy.location("pathname")
            .should(
              "equal",
              `${databaseUri}/definition/public/definitions_table/columns`
            )

          // It should render the README on the overview page.
          cy.getByTestId("ColumnReadme").get("h1").contains("Welcome")
          cy.getByTestId("ColumnReadme").get("h2").contains("Code")
          cy.getByTestId("ColumnReadme").get("pre").contains("var x = 1 + 1")
          cy.getByTestId("ColumnReadme").get("p").contains("This is a test")
          cy.getByTestId("ColumnReadme").get("p").contains("Pretty cool.")
        })
      })

      describe("read access", () => {
        it("does not show the edit button", () => {
          cy.login(readonly.email, readonly.password, workspace.id)
            .then(() => cy.visit(overviewUri))

          cy.getByTestId("ColumnReadme").should("be.visible")
          cy.getByTestId("ColumnReadme.Edit").should("not.be.visible")
        })

        it("redirects out of the README editor", () => {
          cy.login(readonly.email, readonly.password, workspace.id)
            .then(() => cy.visit(`${databaseUri}/definition/public/definitions_table/columns/name/readme/edit`))

          cy.contains("You do not have permission to access this page.").should("be.visible")
        })
      })
    })
  })
})
