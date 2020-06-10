import { AUTH_TOKEN, WORKSPACE_TOKEN } from "../../src/lib/constants"

// Mimic the login prompt form process. This should redirect
// the user to `/login/email` if the email is registered, otherwise it
// will forward to the `/signup` page.
const continueWithEmail = (email) =>{
  cy.getByTestId("LoginPromptForm.Email").type(email)
  cy.contains(
    "button",
    "Continue with Email",
  ).click()
}

describe("authentication.spec.js", () => {
  before(() => {
    cy.resetdb()
  })

  describe("login", () => {
    const validUser = {
      email: "owner@metamapper.io",
      password: "password1234",
    }

    const unregisteredEmail = "karen.vick@sbpd.gov"

    beforeEach(() => {
      cy.visit("/login")
    })

    it("has the correct meta title", () => {
      cy.title().should("eq", "Log In - Metamapper")
    })

    it("requires the correct password", () => {
      continueWithEmail(validUser.email)

      // fill in an INCORRECT password
      cy.getByTestId("LoginForm.Password").type("wrong-password")
      cy.contains("button", "Sign In").click()

      // still on /login page plus an error is displayed
      cy.location("pathname").should("equal", "/login/email")
      cy.contains(".ant-alert.ant-alert-error", "Incorrect login credentials.").should(
        "be.visible"
      )
    })

    it("redirects to sign up when email is not registered", () => {
      continueWithEmail(unregisteredEmail)

      // confirm we get redirected to the sign up page
      cy.location("pathname").should("equal", "/signup")
      cy.contains("Create an Account").should("be.visible")

      // Form should be prefilled based on the URL parameter.
      cy.location("search").should("equal", `?email=${unregisteredEmail}`)
      cy.getByTestId("SignupForm.Email").should("have.value", unregisteredEmail)
    })

    it("fails to access protected resource", () => {
      cy.visit("/")
      cy.location("pathname").should("equal", "/login")
    })

    it("using UI", () => {
      continueWithEmail(validUser.email)

      // fill in the CORRECT password
      cy.getByTestId("LoginForm.Password").type("password1234")
      cy.contains("button", "Sign In").click()

      // confirm we have logged in successfully
      cy.location("pathname").should("equal", "/ctd")
        .then(() => {
          expect(
            window.localStorage.getItem(AUTH_TOKEN)
          ).to.be.a("string")
          expect(
            window.localStorage.getItem(WORKSPACE_TOKEN)
          ).to.be.a("string")
        })

      cy.contains("The search engine for your data.").should("be.visible")
    })
  })

  describe("sign up", () => {
    let existingUserEmail = "owner@metamapper.io"
    let strongPassword = "}~Q9%tu$CnU6>nUE"
    let weakPassword = "password1234"

    beforeEach(() => {
      cy.visit("/signup")
    })

    it("has the correct meta title", () => {
      cy.title().should("eq", "Sign Up - Metamapper")
    })

    it("fails if the user is already registered", () => {
      cy.fillInputs({
        "SignupForm.FirstName": "Sam",
        "SignupForm.LastName": "Crust",
        "SignupForm.Email": existingUserEmail,
        "SignupForm.Password": strongPassword,
      })

      cy.getByTestId("SignupForm.Submit").click()

      cy.location("pathname").should("equal", "/signup")
      cy.contains(".ant-alert.ant-alert-error", "User with this email already exists.").should(
        "be.visible"
      )
    })

    it("fails if the password is too weak", () => {
      cy.fillInputs({
        "SignupForm.FirstName": "Paulie",
        "SignupForm.LastName": "Walnuts",
        "SignupForm.Email": "paulie@sopranos.com",
        "SignupForm.Password": weakPassword,
      })

      cy.getByTestId("SignupForm.Submit").click()

      cy.location("pathname").should("equal", "/signup")

      cy.formHasError(
        "SignupForm.Password",
        "Password is not strong enough.",
      )
    })

    it("using UI", () => {
      cy.fillInputs({
        "SignupForm.FirstName": "Paulie",
        "SignupForm.LastName": "Walnuts",
        "SignupForm.Email": "paulie@sopranos.com",
        "SignupForm.Password": strongPassword,
      })

      cy.getByTestId("SignupForm.Submit").click()

      // It should redirect to the workspaces page. Eventually this should be an onboarding page.
      cy.location("pathname").should("equal", "/workspaces")
        .then(() => {
          expect(
            window.localStorage.getItem(AUTH_TOKEN)
          ).to.be.a("string")
        })
    })
  })

  describe("reset password", () => {
    const validUser = {
      email: "member@metamapper.io",
    }

    const invalidUser = {
      email: "nobody@metamapper.io",
    }

    beforeEach(() => {
      cy.visit("/password/reset")
    })

    it("has the correct meta title", () => {
      cy.title().should("eq", "Reset Your Password - Metamapper")
    })

    it("fails if email does not exist", () => {
      cy.fillInputs({
        "PasswordResetForm.Email": invalidUser.email,
      })

      cy.getByTestId("PasswordResetForm.Submit").click()

      cy.location("pathname").should("equal", "/password/reset")
      cy.contains(
        ".ant-alert.ant-alert-error",
        "We aren't sure if this account exists.",
      ).should(
        "be.visible"
      )
    })

    it("using UI", () => {
      cy.fillInputs({
        "PasswordResetForm.Email": validUser.email,
      })

      cy.getByTestId("PasswordResetForm.Submit").click()

      cy.location("pathname").should("equal", "/password/reset")
      cy.contains(
        ".ant-alert.ant-alert-success",
        "We have sent an email with instructions to reset your password.",
      ).should(
        "be.visible"
      )
    })

  })


  describe("logout", () => {
    beforeEach(() => {
      cy.login().then(() => cy.visit("/"))
    })

    it("shows login page after logout", () => {
      cy.getByTestId("Navbar.Dropdown").click()
      cy.contains("Sign Out").click()

      cy.location("pathname").should("equal", "/login")
      cy.title().should("eq", "Log In - Metamapper")
    })
  })
})
