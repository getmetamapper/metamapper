import React, { useState } from "react"
import { Button, Icon } from "antd"

const EditableText = ({
  content,
  type,
  cypress,
  placeholder,
  children,
  disabled,
  ...props
}) => {
  // Manage the state whether to show the label or the input box. By default, label will be shown.
  // Exercise: It can be made dynamic by accepting initial state as props outside the component
  const [editing, setEditing] = useState(false)

  // Event handler while pressing any key while editing
  const handleKeyDown = (event, type) => {
    // Handle when key is pressed
  }

  const handleClick = (event) => {
    setEditing(false)

    if (props.onClickButton) {
      props.onClickButton(event)
    }
  }

  const handleBlur = (event) => {
    if (props.onBlur) {
      props.onBlur(event)
    }

    setEditing(false)
  }

  const editingProps = {
    onKeyDown: (e) => handleKeyDown(e, type),
  }

  if (props.onBlur) {
    editingProps.onBlur = handleBlur
  }

  return (
    <section {...props} className="editable-text">
      {editing && !disabled ? (
        <div {...editingProps}>
          {children}
          <>
            {props.onClickButton && (
              <Button
                type="primary"
                onClick={handleClick}
                className="ml-10"
                data-test={`${cypress}.Submit`}
              >
                <Icon type="check" />
              </Button>
            )}
          </>
        </div>
      ) : (
        <div
          onClick={() => setEditing(true)}
          className={disabled ? "disabled" : "enabled"}
          data-test={`${cypress}.Container`}
        >
          {content}
        </div>
      )}
    </section>
  )
}

EditableText.defaultProps = {
  disabled: false,
  cypress: "EditableText",
}

export default EditableText
