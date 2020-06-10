import React from "react"
import { render } from "test/utils"
import clientMock from "test/client-mock"

import PasswordConfirm from "./PasswordConfirm"

describe("PasswordConfirm", () => {
  it("renders", () => {
    expect(render(clientMock, PasswordConfirm).find("AuthForm").length).toEqual(
      1
    )
  })
})
