import React from "react"
import { render } from "test/utils"
import clientMock from "test/client-mock"

import PasswordReset from "./PasswordReset"

describe("PasswordReset", () => {
  it("renders", () => {
    expect(render(clientMock, PasswordReset).find("AuthForm").length).toEqual(1)
  })
})
