import React, { Component } from "react"
import { Comment as BaseComment } from "antd"
import Interweave from "interweave"
import moment from "moment"
import UserAvatar from "app/Common/UserAvatar"
import { withWriteAccess } from "hoc/withPermissionsRequired"
import { UpvoteComment, DownvoteComment } from "./VoteForComment"
import CreateComment from "./CreateComment"
import UpdateComment from "./UpdateComment"
import DeleteComment from "./DeleteComment"
import ShareComment from "./ShareComment"
import PinComment from "./PinComment"
import PinnedCommentHeader from "./PinnedCommentHeader"

class Comment extends Component {
  constructor(props) {
    super(props)

    this.state = {
      isCollapsed: !props.isParent || props.childCount > 2,
      isEditing: false,
      isReplying: false,
      numVoteUp: props.numVoteUp,
      numVoteDown: props.numVoteDown,
    }

    this.handleChange = this.handleChange.bind(this)
  }

  toggleReply = () => {
    const isReplying = !this.state.isReplying
    this.setState({ isReplying })

    if (this.props.onCreate) {
      this.props.onCreate()
    }
  }

  toggleEditing = () => {
    const isEditing = !this.state.isEditing
    this.setState({ isEditing })
  }

  toggleCollapsed = () => {
    const isCollapsed = !this.state.isCollapsed
    this.setState({ isCollapsed })
  }

  handleChange = ({ numVoteUp, numVoteDown }) => {
    this.setState({ numVoteUp, numVoteDown })
  }

  renderActions(isParent, isEditing, isCurrentUser) {
    const {
      id,
      isPinned,
      contentObject,
      hasPermission,
      childCount,
      onDelete,
    } = this.props

    const actions = [
      <UpvoteComment
        commentId={id}
        count={this.state.numVoteUp}
        key="comment-upvote"
        onChange={this.handleChange}
      />,
      <DownvoteComment
        commentId={id}
        count={this.state.numVoteDown}
        key="comment-downvote"
        onChange={this.handleChange}
      />,
    ]

    // You can only reply to parent comments.
    if (isParent && hasPermission) {
      actions.push(
        <span key="comment-reply" onClick={this.toggleReply} data-test="Comment.Reply">
          reply
        </span>
      )
    }

    actions.push(<ShareComment key="comment-share" />)

    // You can only pin parent comments if you have write access.
    if (isParent && hasPermission) {
      actions.push(
        <PinComment
          key="comment-pin"
          commentId={id}
          isPinned={isPinned}
          objectId={contentObject.id}
        />
      )
    }

    // You can only collapse comments with children.
    if (isParent) {
      actions.push(
        <span key="comment-collapse" onClick={this.toggleCollapsed}>
          comments ({childCount})
        </span>
      )
    }

    // You can only edit or delete your own comments.
    if (isCurrentUser && hasPermission) {
      actions.push(
        <span key="comment-edit" onClick={this.toggleEditing} data-test="Comment.Edit">
          {isEditing ? "cancel" : "edit"}
        </span>
      )
      actions.push(
        <DeleteComment
          key="comment-delete"
          commentId={id}
          objectId={contentObject.id}
          onSubmit={onDelete}
        />
      )
    }

    return actions
  }

  renderContent(isEditing, commentId, html) {
    const { contentObject, hasPermission } = this.props

    if (isEditing) {
      return (
        <UpdateComment
          commentId={commentId}
          html={html}
          contentObject={contentObject}
          hasPermission={hasPermission}
          onSuccess={this.toggleEditing}
        />
      )
    }

    return <Interweave content={html} />
  }

  render() {
    const { isCollapsed, isEditing, isReplying } = this.state
    const {
      author,
      children,
      contentObject,
      createdAt,
      hasPermission,
      html,
      id,
      isParent,
      isPinned,
      pinnedAt,
      pinnedBy,
    } = this.props
    return (
      <div className={`comment${isPinned ? " pinned" : ""}`}>
        {isPinned && (
          <PinnedCommentHeader pinnedAt={pinnedAt} pinnedBy={pinnedBy} />
        )}
        <BaseComment
          key={id}
          actions={this.renderActions(
            isParent,
            isEditing,
            author.isCurrentUser
          )}
          author={author.name}
          avatar={<UserAvatar {...author} />}
          content={this.renderContent(isEditing, id, html)}
          datetime={moment(createdAt).fromNow()}
        >
          {isReplying && hasPermission && (
            <CreateComment
              parentId={id}
              contentObject={contentObject}
              hasPermission={hasPermission}
              onSubmit={this.toggleReply}
            />
          )}
          {!isCollapsed && children}
        </BaseComment>
      </div>
    )
  }
}

export default withWriteAccess(Comment)
