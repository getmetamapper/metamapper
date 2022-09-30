/* eslint-disable */
import React from "react"
import EnumInput from "./EnumInput"
import MultiSelectInput from "./MultiSelectInput"
import TextInput from "./TextInput"
import UserInput from "./UserInput"
import GroupInput from "./GroupInput"

export const getInputComponent = (customField) => {
  if (!customField) return null

  const switchBoard = {
    TEXT: TextInput,
    ENUM: EnumInput,
    MULTI: MultiSelectInput,
    USER: UserInput,
    GROUP: GroupInput,
  }

  return switchBoard[customField.fieldType]
}
