import React from "react"
import EnumDisplay from "./EnumDisplay"
import MultiSelectDisplay from "./MultiSelectDisplay"
import TextDisplay from "./TextDisplay"
import UserDisplay from "./UserDisplay"
import GroupDisplay from "./GroupDisplay"

export const renderDisplay = (customField, fieldValue) => {
  if (!customField || !fieldValue) return null

  const switchBoard = {
    TEXT: TextDisplay,
    ENUM: EnumDisplay,
    MULTI: MultiSelectDisplay,
    USER: UserDisplay,
    GROUP: GroupDisplay,
  }

  const Component = switchBoard[customField.fieldType]

  return (
    <span data-test={`CustomProperties.Display(${customField.pk})`}>
        <Component value={fieldValue} {...customField} />
    </span>
  )
}
