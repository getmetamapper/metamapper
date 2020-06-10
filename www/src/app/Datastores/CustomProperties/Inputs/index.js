/* eslint-disable */
import React from "react"
import EnumInput from "./EnumInput"
import TextInput from "./TextInput"
import UserInput from "./UserInput"

export const getInputComponent = (customField) => {
  if (!customField) return null

  const switchBoard = {
    TEXT: TextInput,
    ENUM: EnumInput,
    USER: UserInput,
  }

  return switchBoard[customField.fieldType]
}
