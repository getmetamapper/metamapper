
describe("groups.spec.js", () => {
  const workspace = {
    id: "9cd5359c-b062-405c-bb4c-29b074f4d72c",
    name: "Acme Corporation",
    slug: "AcmeCorporation",
  }

  const owner = {
    email: "owner.groups@metamapper.test",
    password: "password1234",
  }

  const member = {
    email: "member.groups@metamapper.test",
    password: "password1234",
  }

  const readonly = {
    email: "readonly.groups@metamapper.test",
    password: "password1234",
  }

  const outsider = {
    email: "outsider.groups@metamapper.test",
    password: "password1234",
  }

  const doesNotHavePermission = [
    { permission: "member", user: member },
    { permission: "readonly", user: readonly },
  ]

  describe("group list", () => {
    it("displays the list of groups", () => {
      cy.login(owner.email, owner.password, workspace.id)
        .then(() =>
          cy.visit(`/${workspace.slug}/settings/groups`))

      cy.title().should("eq", `Groups - ${workspace.slug} - Metamapper`)

      cy.getByTestId("GroupsTable")
        .should("exist")
        .and("contain", "Everybody")
        .and("contain", "Nobody")
        .and("contain", "Executives")
    })
  })

  describe("create group", () => {
    doesNotHavePermission.forEach(({ permission, user }) => {
      it(`is disabled for ${permission} permission`, () => {
        cy.login(user.email, user.password, workspace.id)
          .then(() =>
            cy.visit(`/${workspace.slug}/settings/groups`))

        cy.contains("Add New Group").should("be.disabled")
      })
    })

    describe("as owner", () => {
      beforeEach(() => {
        cy.login(owner.email, owner.password, workspace.id)
          .then(() => cy.visit(`/${workspace.slug}/settings/groups`))
      })

      it("with duplicate name", () => {
        const formInputs = {
          name: "Everybody",
          desc: "",
        }

        cy.contains("Add New Group").click()

        cy.fillInputs({
          "GroupFieldset.Name": formInputs.name,
          "GroupFieldset.Description": formInputs.desc,
        })

        cy.getByTestId("GroupSetupForm.Submit").click()

        cy.contains(".ant-message-error", "Group with that name already exists.").should(
          "be.visible"
        )
      })

      it("with name that is too long", () => {
        const formInputs = {
          name: "This group name is way too long",
          desc: "",
        }

        cy.contains("Add New Group").click()

        cy.fillInputs({
          "GroupFieldset.Name": formInputs.name,
          "GroupFieldset.Description": formInputs.desc,
        })

        cy.getByTestId("GroupSetupForm.Submit").click()

        cy.formHasError(
          "GroupFieldset.Name",
          "This field must be less than 30 characters.",
        )
      })

      it("using UI", () => {
        const formInputs = {
          name: "Tune Squad",
          desc: "The best of the best.",
        }

        cy.contains("Add New Group").click()

        cy.fillInputs({
          "GroupFieldset.Name": formInputs.name,
          "GroupFieldset.Description": formInputs.desc,
        })

        // Submit the form...
        cy.getByTestId("GroupSetupForm.Submit").click()

        cy.contains(".ant-message-success", "Group has been created.").should(
          "be.visible"
        )

        cy.getByTestId("GroupsTable").contains(formInputs.name).parent("tr").within(() => {
          cy.get("td").eq(0).contains(formInputs.name)
          cy.get("td").eq(1).contains("0")
          cy.get("td").eq(2).contains(formInputs.desc)
          cy.get("td").eq(3).contains("Edit")
          cy.get("td").eq(3).contains("Delete")
        })
      })
    })
  })

  describe("update group", () => {
    doesNotHavePermission.forEach(({ permission, user }) => {
      it(`is disabled for ${permission} permission`, () => {
        cy.login(user.email, user.password, workspace.id)
          .then(() =>
            cy.visit(`/${workspace.slug}/settings/groups`))

        cy.getByTestId("GroupsTable").within(() => {
          cy.get("td").eq(1).should("not.have.value", "Edit")
        })
      })
    })

    describe("as owner", () => {
      beforeEach(() => {
        cy.login(owner.email, owner.password, workspace.id)
          .then(() => cy.visit(`/${workspace.slug}/settings/groups`))
      })

      it("using UI", () => {
        cy.getByTestId("GroupsTable").contains("Everybody").parent("tr").within(() => {
          cy.contains("Edit").click()
        })

        const formInputs = {
          name: "Everyone",
          desc: "Everyone in the organization is in this group.",
        }

        cy.fillInputs({
          "GroupFieldset.Name": formInputs.name,
          "GroupFieldset.Description": formInputs.desc,
        })

        cy.getByTestId("UpdateGroupForm.Submit").click()

        cy.contains(".ant-message-success", "Group has been updated.").should(
          "be.visible"
        )

        cy.getByTestId("GroupsTable").contains(formInputs.name).parent("tr").within(() => {
          cy.get("td").eq(0).contains(formInputs.name)
          cy.get("td").eq(1).contains("7")
          cy.get("td").eq(2).contains(formInputs.desc)
          cy.get("td").eq(3).contains("Edit")
          cy.get("td").eq(3).contains("Delete")
        })
      })
    })
  })

  describe("remove group", () => {
    doesNotHavePermission.forEach(({ permission, user }) => {
      it(`is disabled for ${permission} permission`, () => {
        cy.login(user.email, user.password, workspace.id)
          .then(() =>
            cy.visit(`/${workspace.slug}/settings/groups`))

        cy.getByTestId("GroupsTable").within(() => {
          cy.get("td").eq(3).should("not.have.value", "Delete")
        })
      })
    })

    describe("as owner", () => {
      beforeEach(() => {
        cy.login(owner.email, owner.password, workspace.id)
          .then(() => cy.visit(`/${workspace.slug}/settings/groups`))
      })

      it("using UI", () => {
        cy.getByTestId("GroupsTable").contains("Executives").parent("tr").within(() => {
          cy.contains("Delete").click()
        })

        cy.getByTestId("DeleteGroup.ConfirmationPrompt").should("be.visible")
        cy.getByTestId("DeleteGroup.Submit").should("be.visible").should("be.disabled")

        // Typing the wrong words doesn't do anything.
        cy.fillInputs({
          "DeleteGroup.ConfirmationPrompt": "incorrect"
        })
        cy.getByTestId("DeleteGroup.Submit").should("be.disabled")

        // Typing the right words enables the deletion prompt.
        cy.fillInputs({
          "DeleteGroup.ConfirmationPrompt": "delete me"
        })
        cy.getByTestId("DeleteGroup.Submit").click()

        cy.contains(".ant-message-success", "Group has been removed.").should(
          "be.visible"
        )

        cy.getByTestId("GroupsTable").should("exist").and("not.contain", "Executives")
      })
    })
  })

  describe("view group users", () => {
    beforeEach(() => {
      cy.login(owner.email, owner.password, workspace.id)
        .then(() => cy.visit(`/${workspace.slug}/settings/groups`))
    })

    it("displays a paginated list of users", () => {
      cy.getByTestId("GroupsTable").contains("Everyone").parent("tr").within(() => {
        cy.get("td").eq(1).click()
      })

      cy.getByTestId("GroupUsersTable")
        .should("exist")
        .and("contain", "Bugs Bunny")
        .and("contain", "Daffy Duck")
        .and("contain", "Elmer Fudd")

      cy.getByTestId("GroupUsersTable").get(".user-display-name").should("have.length", 5)
    })

    it("filters users via search", () => {
      cy.getByTestId("GroupsTable").contains("Everyone").parent("tr").within(() => {
        cy.get("td").eq(1).click()
      })

      cy.getByTestId("GroupUsersTable")
        .should("exist")
        .and("contain", "Bugs Bunny")
        .and("contain", "Daffy Duck")
        .and("contain", "Elmer Fudd")

      cy.getByTestId("GroupUsersTable").get(".user-display-name").should("have.length", 5)

      cy.getByTestId("GroupUsersTable.SearchIcon").click()

      cy.fillInputs({
        "GroupUsersTable.SearchInput": "Bugs",
      })

      cy.getByTestId("GroupUsersTable.SearchSubmit").click()

      cy.getByTestId("GroupUsersTable")
        .should("exist")
        .and("contain", "Bugs Bunny")

      cy.getByTestId("GroupUsersTable").get(".user-display-name").should("have.length", 1)
    })
  })

  describe("remove user from group", () => {
    beforeEach(() => {
      cy.login(owner.email, owner.password, workspace.id)
        .then(() => cy.visit(`/${workspace.slug}/settings/groups`))
    })

    it("using UI", () => {
      const targetUser = "Bugs Bunny"

      cy.getByTestId("GroupsTable").contains("Everyone").parent("tr").within(() => {
        cy.get("td").eq(1).click()
      })

      cy.getByTestId("GroupUsersTable").within(() => {
        cy.contains("Remove").click()
      })

      cy.contains(".ant-message-success", "User has been removed from the group.").should(
        "be.visible"
      )

      cy.getByTestId("GroupUsersTable").should("exist").and("not.contain", targetUser)
      cy.getByTestId("GroupUsersTable").get(".user-display-name").should("have.length", 5)
    })
  })

  describe("add user to group", () => {
    beforeEach(() => {
      cy.login(owner.email, owner.password, workspace.id)
        .then(() => cy.visit(`/${workspace.slug}/settings/groups`))
    })

    it("using UI", () => {
      const targetUser = "Bugs Bunny"

      cy.getByTestId("GroupsTable").contains("Everyone").parent("tr").within(() => {
        cy.get("td").eq(1).click()
      })

      cy.fillInputs({
        "AddUserToGroupForm.Input": targetUser
      })

      cy.getByTestId("AddUserToGroupForm.Submit").click()

      cy.contains(".ant-message-success", "User has been added to the group.").should(
        "be.visible"
      )

      cy.getByTestId("GroupUsersTable").should("exist").and("contain", targetUser)
      cy.getByTestId("GroupUsersTable").get(".user-display-name").should("have.length", 5)
    })
  })

  describe("404", () => {
    it("when workspace does not exist", () => {
      cy.login(owner.email, owner.password)
        .then(() =>
          cy.visit("/does-not-exist/settings/groups"))

      cy.contains("Sorry, the page you are looking for doesn't exist.").should("be.visible")
    })

    it("when user is unauthorized", () => {
      cy.login(outsider.email, outsider.password)
        .then(() =>
          cy.visit(`/${workspace.slug}/settings/groups`))

      cy.contains("Sorry, the page you are looking for doesn't exist.").should("be.visible")
    })
  })
})
