import React, { Component } from "react"
import { graphql, compose } from "react-apollo"
import { Card, Form, Empty, Tooltip } from "antd"
import { map, keyBy } from "lodash"
import { withWriteAccess } from "hoc/withPermissionsRequired"
import GetCustomProperties from "graphql/queries/GetCustomProperties"
import UpdateCustomPropertiesMutation from "graphql/mutations/UpdateCustomProperties"
import withGraphQLMutation from "hoc/withGraphQLMutation"
import withLoader from "hoc/withLoader"
import withGetCustomFields from "graphql/withGetCustomFields"
import withGetCustomPropertyUsers from "graphql/withGetCustomPropertyUsers"
import CustomPropertiesFooter from "./CustomPropertiesFooter"
import CustomPropertiesHeader from "./CustomPropertiesHeader"
import { renderDisplay } from "./Displays"
import { getInputComponent } from "./Inputs"

class UpdateCustomProperties extends Component {
  constructor(props) {
    super(props)

    this.state = {
      isEditing: false,
    }
  }

  handleToggleEdit = () => {
    this.setState({ isEditing: !this.state.isEditing })
  }

  handleSubmit = (evt) => {
    evt.preventDefault()

    this.props.form.validateFields((err, variables) => {
      if (err) return

      const {
        contentObject: { id: objectId },
      } = this.props
      const properties = Object.keys(variables).map(function (id) {
        return {
          id,
          value: variables[id],
        }
      })

      const payload = {
        variables: {
          objectId,
          properties,
        },
        successMessage: "Properties have been updated.",
        refetchQueries: [
          {
            query: GetCustomProperties,
            variables: {
              objectId,
            },
          },
        ],
      }

      this.props.handleMutation(payload, this.handleSubmitSuccess)
    })
  }

  handleSubmitSuccess = ({ data }) => {
    const {
      updateCustomProperties: { errors },
    } = data

    if (!errors) {
      this.setState({ isEditing: false })
    }
  }

  renderLabel(field) {
    if (!field) return null
    return (
      <Tooltip title={field.shortDesc}>
        <span className="label" data-test={`CustomProperties.Label(${field.pk})`}>
          {field.fieldName}
        </span>
      </Tooltip>
    )
  }

  render() {
    const { isEditing } = this.state
    const {
      customFields,
      customProperties,
      form,
      hasPermission,
      submitting,
      users,
    } = this.props
    const fields = keyBy(customFields, "pk")
    return (
      <Card
        title="Properties"
        extra={
          <CustomPropertiesHeader
            isEditable={customProperties.length > 0 && hasPermission}
            onToggleEdit={this.handleToggleEdit}
          />
        }
      >
        <Form
          className="custom-fields-form"
          labelCol={{ span: 7 }}
          wrapperCol={{ span: 17 }}
          onSubmit={this.handleSubmit}
        >
          {customProperties.length === 0 ? (
            <Empty />
          ) : (
            <>
              {map(customProperties, ({ fieldId, fieldLabel, fieldValue }) => {
                const field = fields[fieldId]
                if (!field) return null
                if (!isEditing && !fieldValue) return null
                const InputComponent = getInputComponent(field)
                const inputProps = {
                  form,
                  field,
                  initialValue: fieldValue,
                }
                if (fields[fieldId].fieldType === "USER") {
                  inputProps.choices = users
                } else if (fields[fieldId].fieldType === "ENUM") {
                  inputProps.choices = field.validators.choices
                }
                return (
                  <div className="custom-property">
                    <div className="labelWrap clearfix">
                      {this.renderLabel(fields[fieldId])}
                    </div>
                    <div className="valueWrap clearfix">
                      {isEditing ? (
                        <InputComponent {...inputProps} />
                      ) : (
                        renderDisplay(fields[fieldId], fieldValue)
                      )}
                    </div>
                  </div>
                )
              })}
              {isEditing && hasPermission && (
                <CustomPropertiesFooter
                  isSubmitting={submitting}
                  onCancel={this.handleToggleEdit}
                />
              )}
            </>
          )}
        </Form>
      </Card>
    )
  }
}

const withLargeLoader = withLoader({
  size: "large",
  wrapperstyles: {
    textAlign: "center",
    marginTop: "40px",
    marginBottom: "40px",
  },
})

const withForm = Form.create()

const enhance = compose(
  withLargeLoader,
  withForm,
  withWriteAccess,
  withGetCustomFields,
  withGetCustomPropertyUsers,
  graphql(UpdateCustomPropertiesMutation),
  withGraphQLMutation
)

export default enhance(UpdateCustomProperties)
