import React, { Component } from "react"
import { compose, graphql } from "react-apollo"
import { Card } from "antd"
import { map } from "lodash"
import TableOwnersHeader from "./TableOwnersHeader"
import TableOwnerInput from "./TableOwnerInput"
import DraggableList from "app/Common/DraggableList"
import UpdateAssetOwner from "graphql/mutations/UpdateAssetOwner"
import withGraphQLMutation from "hoc/withGraphQLMutation"

class TableOwners extends Component {
  constructor(props) {
    super(props)

    this.state = {
      isEditing: false,
      owners: props.tableDefinition.owners,
    }

    this.handleReposition = this.handleReposition.bind(this)

    this.draggableProps = {
      onDragEnd: this.handleReposition,
      nodeSelector: 'li',
      handleSelector: 'li',
    }
  }

  componentWillReceiveProps(nextProps) {
    let { isEditing } = this.state
    const { tableDefinition: { owners } } = nextProps

    if (isEditing && owners.length === 0) {
      isEditing = false
    }

    this.setState({ owners, isEditing })
  }

  shouldComponentUpdate(nextProps, nextState) {
    return this.state.owners.length !== nextState.owners.length ||
      this.state.isEditing !== nextState.isEditing ||
      this.state.orderChanged !== nextState.orderChanged ||
      this.state.owners.length !== nextState.owners.length
  }

  handleToggleEdit = () => {
    this.setState({ isEditing: !this.state.isEditing })
  }

  handleReposition = (fromIndex, toIndex) => {
    const owners = [...this.state.owners]
    const item = owners.splice(fromIndex, 1)[0]
    owners.splice(toIndex, 0, item)
    this.setState({ owners, orderChanged: Math.random() })

    const payload = {
      variables: { id: item.id, order: toIndex },
      successMessage: null,
      refetchQueries: ["GetTableDefinitionWithOwners"],
    }

    this.props.handleMutation(payload)
  }

  isEmpty() {
    return this.state.owners && this.state.owners.length === 0
  }

  render() {
    const { isEditing, owners } = this.state
    const { hasPermission, tableDefinition: { id: objectId } } = this.props
    const isEmpty = this.isEmpty()
    return (
      <div className={`table-owners ${isEmpty && 'empty'}`} data-test="TableOwners">
        <Card title="Owners" extra={
          <TableOwnersHeader
            isEditing={isEditing}
            isEditable={hasPermission}
            isEmpty={isEmpty}
            objectId={objectId}
            ownerIds={map(owners, ({ owner }) => owner.id)}
            onToggleEdit={this.handleToggleEdit}
          />
        }>
          {isEmpty && !isEditing ? ( <div className="empty-text">No owners assigned.</div> ) : (
            <DraggableList enabled={isEditing} {...this.draggableProps}>
              {map(owners, ({ id, type, classification, order, owner }) => (
                <li className={isEditing ? 'table-owner editing' : 'table-owner'}>
                  <TableOwnerInput
                    isEditing={isEditing}
                    ownerId={id}
                    owner={owner}
                    type={type}
                    classification={classification}
                  />
                </li>
              ))}
            </DraggableList>
          )}
        </Card>
      </div>
    )
  }
}

export default compose(
  graphql(UpdateAssetOwner),
  withGraphQLMutation
)(TableOwners)
