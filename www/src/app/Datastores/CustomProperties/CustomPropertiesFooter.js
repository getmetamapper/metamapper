import React from "react"
import { Button } from "antd"

const CustomPropertiesFooter = ({ isSubmitting, onCancel }) => (
  <div className="custom-fields-edit-actions">
    <Button type="default" onClick={onCancel} data-test="CustomProperties.Cancel">
      Cancel
    </Button>
    <Button
        type="primary"
        htmlType="submit"
        disabled={isSubmitting}
        data-test="CustomProperties.Submit"
    >
      {isSubmitting ? "Saving..." : "Save all"}
    </Button>
  </div>
)

export default CustomPropertiesFooter
