import { DEFAULT_WORKSPACE_SLUG } from "../support/constants"

describe("user.spec.js", () => {
  before(() => {
    cy.resetdb()
  })

  describe("edit user profile", () => {
    let email = "readonly@metamapper.io"

    beforeEach(() => {
      cy.login(email, "password1234")
        .then(() => cy.visit(`/${DEFAULT_WORKSPACE_SLUG}`).wait(1000))

      cy.getByTestId("Navbar.Dropdown").click()

      cy.contains("User Settings").click();
      cy.contains("Profile").click();
    })

    it("requires a password", () => {
      cy.fillInputs({
        "UpdateUserProfileForm.FirstName": "Burton",
        "UpdateUserProfileForm.LastName": "Guster",
        "UpdateUserProfileForm.Email": email,
      })

      cy.getByTestId("UpdateUserProfileForm.Submit").click()

      cy.get(".has-error #currentPassword").should("be.visible")
      cy.contains(".ant-form-explain", "This field is required.").should(
        "be.visible"
      )
    })

    it("requires a correct password", () => {
      cy.fillInputs({
        "UpdateUserProfileForm.FirstName": "Burton",
        "UpdateUserProfileForm.LastName": "Guster",
        "UpdateUserProfileForm.Email": email,
        "UpdateUserProfileForm.CurrentPassword": "bananas",
      })

      cy.getByTestId("UpdateUserProfileForm.Submit").click()

      cy.get(".ant-message-notice").should("be.visible")
      cy.contains(".ant-message-error", "The password you provided is incorrect.").should(
        "be.visible"
      )
    })

    const formValidationFixtures = [
      {
        describe: "validates required fields",
        inputs: {
          "Email": { value: "", error: "This field is required." },
          "FirstName": { value: "", error: "This field is required." },
          "LastName": { value: "", error: "This field is required." },
        },
      },
      {
        describe: "validates email format",
        inputs: {
          "Email": { value: "guster.com", error: "Email format is invalid." },
          "FirstName": { value: "Burton", error: null },
          "LastName": { value: "Guster", error: null },
        },
      },
      {
        describe: "validate name length",
        inputs: {
          "Email": { value: email, error: null },
          "FirstName": {
            value: (Math.random()*1e256).toString(36),
            error: "This field must be less than 60 characters.",
          },
          "LastName": {
            value: (Math.random()*1e256).toString(36),
            error: "This field must be less than 60 characters.",
          },
        },
      },
    ]

    formValidationFixtures.forEach(({ describe, inputs }) => {
      it(describe, () => {
        cy.fillInputs({
          "UpdateUserProfileForm.FirstName": inputs["FirstName"]["value"],
          "UpdateUserProfileForm.LastName": inputs["LastName"]["value"],
          "UpdateUserProfileForm.Email": inputs["Email"]["value"],
          "UpdateUserProfileForm.CurrentPassword": "password1234",
        })

        cy.getByTestId("UpdateUserProfileForm.Submit").click()

        cy.verifyFormErrors("UpdateUserProfileForm", inputs)
      })
    })

    it("requires a unique email address", () => {
      cy.fillInputs({
        "UpdateUserProfileForm.FirstName": "Gary",
        "UpdateUserProfileForm.LastName": "Scott",
        "UpdateUserProfileForm.Email": "michael.scott@metamapper.io",
        "UpdateUserProfileForm.CurrentPassword": "password1234",
      })

      cy.getByTestId("UpdateUserProfileForm.Submit").click()

      cy.get(".ant-message-notice").should("be.visible")
      cy.contains(".ant-message-error", "User with this email already exists.").should(
        "be.visible"
      )

      cy.reload()

      cy.getByTestId("Navbar.Dropdown").click()
      cy.contains("User Settings").click();

      cy.getByTestId("UpdateUserProfileForm.FirstName").should(
        "not.have.value",
        "Gary",
      )

      cy.getByTestId("UpdateUserProfileForm.LastName").should(
        "not.have.value",
        "Scott",
      )

      cy.getByTestId("UpdateUserProfileForm.Email").should(
        "not.have.value",
        "michael.scott@metamapper.io",
      )
    })

    it("using UI", () => {
      cy.fillInputs({
        "UpdateUserProfileForm.FirstName": "Burton",
        "UpdateUserProfileForm.LastName": "Guster",
        "UpdateUserProfileForm.Email": "burton.guster@metamapper.io",
        "UpdateUserProfileForm.CurrentPassword": "password1234",
      })

      cy.getByTestId("UpdateUserProfileForm.Submit").click()

      cy.get(".ant-message-notice").should("be.visible")
      cy.contains(".ant-message-success", "Your profile has been updated.").should(
        "be.visible"
      )

      cy.reload()

      cy.getByTestId("Navbar.Dropdown").click()
      cy.contains("User Settings").click();

      cy.getByTestId("UpdateUserProfileForm.FirstName").should("have.value", "Burton")
      cy.getByTestId("UpdateUserProfileForm.LastName").should("have.value", "Guster")
      cy.getByTestId("UpdateUserProfileForm.Email").should(
        "have.value",
        "burton.guster@metamapper.io",
      )
    })
  })

  describe("edit user password", () => {
    let email = "owner@metamapper.io"

    const passwords = {
      current: "password1234",
      newSafe: "Ccbc;gNr$-L+6@Z]",
      newWeak: "banana",
      incorrect: "password54321",
    }

    beforeEach(() => {
      cy.login(email, "password1234")
        .then(() => cy.visit(`/${DEFAULT_WORKSPACE_SLUG}`).wait(1000))

      cy.getByTestId("Navbar.Dropdown").click()

      cy.contains("User Settings").click();
      cy.contains("Security").click();
    })

    it("requires the correct current password", () => {
      cy.fillInputs({
        "UpdatePasswordForm.CurrentPassword": passwords.incorrect,
        "UpdatePasswordForm.NewPassword": passwords.newSafe,
        "UpdatePasswordForm.ConfirmPassword": passwords.newSafe,
      })

      cy.getByTestId("UpdatePasswordForm.Submit").click()
      cy.getByTestId("UpdatePasswordForm.Submit").should("be.disabled")

      cy.get(".ant-message-notice").should("be.visible")
      cy.contains(".ant-message-error", "The password you provided is incorrect.").should(
        "be.visible"
      )
    })

    it("requires the password and the confirmation to match", () => {
      cy.fillInputs({
        "UpdatePasswordForm.CurrentPassword": passwords.current,
        "UpdatePasswordForm.NewPassword": passwords.newSafe,
        "UpdatePasswordForm.ConfirmPassword": passwords.newSafe + "x",
      })

      cy.getByTestId("UpdatePasswordForm.Submit").click()

      cy.get(".has-error #confirmPassword").should("be.visible")
      cy.contains(".ant-form-explain", "Confirmation must match new password.").should(
        "be.visible"
      )
    })

    it("requires a strong password", () => {
      cy.fillInputs({
        "UpdatePasswordForm.CurrentPassword": passwords.current,
        "UpdatePasswordForm.NewPassword": passwords.newWeak,
        "UpdatePasswordForm.ConfirmPassword": passwords.newWeak,
      })

      cy.getByTestId("UpdatePasswordForm.Submit").click()

      cy.get(".has-error [data-test=\"UpdatePasswordForm.NewPassword\"]").should("be.visible")
      cy.contains(".ant-form-explain", "Password is not strong enough.").should(
        "be.visible"
      )
    })

    it("using UI", () => {

      cy.fillInputs({
        "UpdatePasswordForm.CurrentPassword": passwords.current,
        "UpdatePasswordForm.NewPassword": passwords.newSafe,
        "UpdatePasswordForm.ConfirmPassword": passwords.newSafe,
      })

      cy.getByTestId("UpdatePasswordForm.Submit").click()
      cy.getByTestId("UpdatePasswordForm.Submit").should("be.disabled")

      cy.get(".ant-message-notice").should("be.visible")
      cy.contains(".ant-message-success", "Your password has been changed.").should(
        "be.visible"
      )

      // It should clear the form.
      cy.getByTestId("UpdatePasswordForm.CurrentPassword").should("have.value", "")
      cy.getByTestId("UpdatePasswordForm.NewPassword").should("have.value", "")
      cy.getByTestId("UpdatePasswordForm.ConfirmPassword").should("have.value", "")

      // It should keep the user logged in.
      cy.reload()
      cy.contains("The search engine for your data.").should("be.visible")

      // It should allow the user to log in with the new password.
      cy.logout()
      cy.location("pathname").should("equal", "/login")

      cy.getByTestId("LoginPromptForm.Email").type(email)
      cy.contains("button", "Continue with Email").click()

      cy.getByTestId("LoginForm.Password").type(passwords.newSafe)
      cy.contains("button", "Sign In").click()

      cy.contains("The search engine for your data.").should("be.visible")
    })
  })
})
