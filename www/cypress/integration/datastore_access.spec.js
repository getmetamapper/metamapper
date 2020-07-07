
describe("datastore_access.spec.js", () => {
  const datastore = {
    name: 'Metamapper',
    slug: 'metamapper',
  }

  const workspace = {
    id: "d6acb067-4751-4d17-b74f-21e7b00c95a4",
    slug: "gcc",
  }

  const otherWorkspace = {
    id: "acdda298-cf05-476a-9a09-d5e3ae7f02a8",
    slug: "nbc",
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
    name: "Shirley Bennett",
    email: "readonly.definitions@metamapper.test",
    password: "password1234",
  }

  const outsider = {
    email: "outsider.definitions@metamapper.test",
    password: "password1234",
  }

  const group = {
    name: "Analytics"
  }

  const availablePrivileges = [
    "View Datastore",
    "Change Datastore Settings",
    "Change Datastore Connection",
    "Change Datastore Metadata",
    "Comment on Datastore",
    "Change Datastore Access",
  ]

  const dataRootUri = `/${workspace.slug}/datastores`
  const databaseUri = `${dataRootUri}/${datastore.slug}`

  const navigateToAccessPage = (user) => {
    cy.login(user.email, user.password, workspace.id).then(() => cy.visit(databaseUri))
    cy.contains("Access").click()
  }

  const testGrantingPermission = (type, targetUser, privileges) => {
    cy.getByTestId(`Grant${type}AccessButton`).click()
    cy.getByTestId(`GrantDatastore${type}AccessForm`).should("be.visible")

    const inputs = {}
    inputs[`GrantDatastore${type}AccessForm.ObjectId`] = targetUser.name

    cy.fillInputs(inputs)

    for (var i = privileges.length - 1; i >= 0; i--) {
      cy.contains(privileges[i]).click()
    }

    cy.getByTestId(`GrantDatastore${type}AccessForm.Submit`).click()
    cy.contains(".ant-message-success", "Changes have been saved.").should(
      "be.visible"
    )

    cy.get(".ant-modal-close-x").click()

    cy.getByTestId(`DatastoreAccess${type}PrivilegesTable`).should("be.visible").should("contain", targetUser.name)
    cy.getByTestId(`DatastoreAccess${type}PrivilegesTable`).should("be.visible")

    cy.getByTestId(`DatastoreAccess${type}PrivilegesTable`).contains(targetUser.name).parent().parent("tr").within(() => {
      for (var i = availablePrivileges.length - 1; i >= 0; i--) {
        let isChecked = privileges.indexOf(availablePrivileges[i]) > -1
        cy.get("td").eq(i + 1).find("i")
                          .should("be.visible")
                          .should("have.class", (isChecked) ? "anticon-check-circle" : "anticon-close-circle")
      }
    })
  }

  const testUpdatingPermissions = (type, targetUser, privileges) => {
    cy.getByTestId(`DatastoreAccess${type}PrivilegesTable`).contains(targetUser.name).parent().parent("tr").within(() => {
      cy.contains("Edit").click()

      for (var i = availablePrivileges.length - 1; i >= 0; i--) {
        cy.get("td").eq(availablePrivileges.indexOf(privileges[i]) + 1).click()
      }

      cy.contains("Save").click()
    })

    cy.contains(".ant-message-success", "Changes have been saved.").should(
      "be.visible"
    )
  }

  const testRevokePermissions = (type, targetUser) => {
    cy.getByTestId(`DatastoreAccess${type}PrivilegesTable`).contains(targetUser.name).parent().parent("tr").within(() => {
      cy.contains("Remove").click()
    })

    // Are you sure?
    cy.contains("Yes").click()

    // Confirmation message should display.
    cy.contains(".ant-message-success", "Changes have been saved.").should(
      "be.visible"
    )

    cy.getByTestId(`DatastoreAccess${type}PrivilegesTable`).should("be.visible").should("not.contain", targetUser.name)
  }

  describe("setup", () => {
    beforeEach(() => navigateToAccessPage(owner))

    it("can enable limited access", () => {
      cy.getByTestId("ToggleDatastoreObjectPermissions").click()
      cy.wait(1000)
      cy.getByTestId("ToggleDatastoreObjectPermissions").should("have.class", "ant-switch-checked")
    })
  })

  describe("add group permissions", () => {
    describe("as owner", () => {
      beforeEach(() => navigateToAccessPage(owner))

      it("can execute properly", () => {
        const privileges = [
          "View Datastore",
          "Change Datastore Metadata",
          "Change Datastore Settings",
          "Change Datastore Access",
        ]

        testGrantingPermission("Group", group, privileges)
      })
    })
  })

  describe("update group permissions", () => {
    describe("as owner", () => {
      beforeEach(() => navigateToAccessPage(owner))

      it("can execute properly", () => {
        const privileges = [
          "View Datastore", // disables
          "Change Datastore Metadata", // disables
          "Change Datastore Connection",
        ]

        testUpdatingPermissions("Group", group, privileges)

        cy.getByTestId(`DatastoreAccessGroupPrivilegesTable`).contains(group.name).parent().parent("tr").within(() => {
          cy.get("td").eq(1).find("i").should("have.class", "anticon-close-circle")
          cy.get("td").eq(2).find("i").should("have.class", "anticon-check-circle")
          cy.get("td").eq(3).find("i").should("have.class", "anticon-check-circle")
          cy.get("td").eq(4).find("i").should("have.class", "anticon-close-circle")
          cy.get("td").eq(5).find("i").should("have.class", "anticon-close-circle")
          cy.get("td").eq(6).find("i").should("have.class", "anticon-check-circle")
        })
      })
    })
  })

  describe("remoke all group permissions", () => {
    describe("as owner", () => {
      beforeEach(() => navigateToAccessPage(owner))

      it("can revoke all permissions", () => {
        testRevokePermissions("Group", group)
      })
    })
  })

  describe("add user permissions", () => {
    describe("as owner", () => {
      beforeEach(() => navigateToAccessPage(owner))

      it("can execute properly", () => {
        const privileges = [
          "View Datastore",
          "Change Datastore Settings",
          "Change Datastore Access",
        ]

        testGrantingPermission("User", otherMember, privileges)
      })
    })

    describe("as permitted member", () => {
      beforeEach(() => navigateToAccessPage(otherMember))

      it("can execute properly", () => {
        const privileges = [
          "View Datastore",
          "Change Datastore Metadata",
          "Change Datastore Access",
          "Comment on Datastore",
        ]

        testGrantingPermission("User", readonly, privileges)
      })
    })

    describe("readonly", () => {
      beforeEach(() => navigateToAccessPage(readonly))

      it("cannot alter permissions", () => {
        cy.getByTestId("GrantUserAccessButton").click()
        cy.getByTestId("GrantDatastoreUserAccessForm").should("be.visible")

        cy.fillInputs({
          "GrantDatastoreUserAccessForm.ObjectId": owner.name,
        })

        const privileges = [
          "View Datastore",
          "Change Datastore Metadata",
        ]

        for (var i = privileges.length - 1; i >= 0; i--) {
          cy.contains(privileges[i]).click()
        }

        cy.getByTestId("GrantDatastoreUserAccessForm.Submit").click()

        cy.contains(".ant-message-error", "You do not have permission to perform this action.").should(
          "be.visible"
        )

        cy.getByTestId("DatastoreAccessUserPrivilegesTable").should("be.visible").should("not.contain", owner.name)
      })
    })
  })

  describe("update user permissions", () => {
    describe("as owner", () => {
      beforeEach(() => navigateToAccessPage(owner))

      it("can execute properly", () => {
        const privileges = [
          "View Datastore",
          "Change Datastore Metadata",
          "Comment on Datastore",
        ]

        testUpdatingPermissions("User", readonly, privileges)

        cy.getByTestId(`DatastoreAccessUserPrivilegesTable`).contains(readonly.name).parent().parent("tr").within(() => {
          cy.get("td").eq(1).find("i").should("have.class", "anticon-close-circle")
          cy.get("td").eq(2).find("i").should("have.class", "anticon-close-circle")
          cy.get("td").eq(3).find("i").should("have.class", "anticon-close-circle")
          cy.get("td").eq(4).find("i").should("have.class", "anticon-close-circle")
          cy.get("td").eq(5).find("i").should("have.class", "anticon-close-circle")
          cy.get("td").eq(6).find("i").should("have.class", "anticon-check-circle")
        })
      })
    })

    describe("as permitted member", () => {
      beforeEach(() => navigateToAccessPage(otherMember))

      it("can execute properly", () => {
        const privileges = [
          "View Datastore",
          "Change Datastore Metadata",
          "Change Datastore Access",
        ]

        testUpdatingPermissions("User", readonly, privileges)

        cy.getByTestId("DatastoreAccessUserPrivilegesTable").contains(readonly.name).parent().parent("tr").within(() => {
          cy.get("td").eq(1).find("i").should("have.class", "anticon-check-circle")
          cy.get("td").eq(2).find("i").should("have.class", "anticon-close-circle")
          cy.get("td").eq(3).find("i").should("have.class", "anticon-close-circle")
          cy.get("td").eq(4).find("i").should("have.class", "anticon-check-circle")
          cy.get("td").eq(5).find("i").should("have.class", "anticon-close-circle")
          cy.get("td").eq(6).find("i").should("have.class", "anticon-close-circle")
        })
      })
    })
  })

  describe("remoke all user permissions", () => {
    describe("as permitted member", () => {
      beforeEach(() => navigateToAccessPage(otherMember))

      it("can revoke all permissions", () => {
        testRevokePermissions("User", readonly)
      })
    })

    describe("as owner", () => {
      beforeEach(() => navigateToAccessPage(owner))

      it("can revoke all permissions", () => {
        testRevokePermissions("User", otherMember)
      })
    })
  })

  describe("404", () => {
    it("when workspace does not exist", () => {
      cy.login(owner.email, owner.password, workspace.id)
        .then(() =>
          cy.visit("/does-not-exist/datastores/show-me/access"))

      cy.contains("Sorry, the page you are looking for doesn't exist.").should("be.visible")
    })

    it("when datastore does not exist", () => {
      cy.login(owner.email, owner.password, workspace.id)
        .then(() =>
          cy.visit(`/${workspace.slug}/datastores/show-me/access`))

      cy.contains("Sorry, the page you are looking for doesn't exist.").should("be.visible")
    })

    it("when member does not have permissions", () => {
      cy.login(otherMember.email, otherMember.password, workspace.id)
        .then(() =>
          cy.visit(`${databaseUri}/access`))

      cy.contains("Sorry, the page you are looking for doesn't exist.").should("be.visible")
    })

    it("when member is not in workspace", () => {
      cy.login(outsider.email, outsider.password, workspace.id)
        .then(() =>
          cy.visit(`${databaseUri}/access`))

      cy.contains("Sorry, the page you are looking for doesn't exist.").should("be.visible")
    })
  })

  describe("teardown", () => {
    beforeEach(() => navigateToAccessPage(owner))

    it("can enable limited access", () => {
      cy.getByTestId("ToggleDatastoreObjectPermissions").click()
      cy.wait(1000)
      cy.getByTestId("ToggleDatastoreObjectPermissions").should("not.have.class", "ant-switch-checked")
    })
  })
})
