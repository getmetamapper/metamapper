import ReactDragListView from './ReactDragListView';

const UNIT_PX = 'px';
const DRAG_LIND_STYLE = 'width:0;margin-left:-1px;margin-top:0;' +
                        'border-bottom:0 none;border-left:dashed 2px red;';
const DIRECTIONS = {
  RIGHT: 2,
  LEFT: 4
};

class ReactDragColumnView extends ReactDragListView {
  getDragLine() {
    if (!this.dragLine) {
      super.getDragLine();
      this.dragLine.setAttribute('style', this.dragLine.getAttribute('style') + DRAG_LIND_STYLE);
    }
    return this.dragLine;
  }

  resolveAutoScroll(e, target) {
    if (!this.scrollElement) {
      return;
    }
    const { left, width } = this.scrollElement.getBoundingClientRect();
    const targetWidth = target.offsetWidth;
    const { pageX } = e;
    const compatibleWidth = (targetWidth * 2) / 3;
    this.direction = 0;
    if (pageX > ((left + width) - compatibleWidth)) {
      this.direction = DIRECTIONS.RIGHT;
    } else if (pageX < (left + compatibleWidth)) {
      this.direction = DIRECTIONS.LEFT;
    }
    if (this.direction) {
      if (this.scrollTimerId < 0) {
        this.scrollTimerId = setInterval(this.autoScroll, 20);
      }
    } else {
      this.stopAutoScroll();
    }
  }

  autoScroll() {
    const { scrollLeft } = this.scrollElement;
    if (this.direction === DIRECTIONS.RIGHT) {
      this.scrollElement.scrollLeft = scrollLeft + this.props.scrollSpeed;
      if (scrollLeft === this.scrollElement.scrollLeft) {
        this.stopAutoScroll();
      }
    } else if (this.direction === DIRECTIONS.LEFT) {
      this.scrollElement.scrollLeft = scrollLeft - this.props.scrollSpeed;
      if (this.scrollElement.scrollLeft <= 0) {
        this.stopAutoScroll();
      }
    } else {
      this.stopAutoScroll();
    }
  }

  fixDragLine(target) {
    const dragLine = this.getDragLine();
    if (!target || this.state.fromIndex < 0
        || this.state.fromIndex === this.state.toIndex) {
      this.hideDragLine();
      return;
    }
    const {
      left, top, width, height
    } = target.getBoundingClientRect();
    const lineLeft = (this.state.toIndex < this.state.fromIndex
      ? left
      : (left + width));
    if (this.props.enableScroll && this.scrollElement) {
      const {
        width: scrollWidth,
        left: scrollLeft
      } = this.scrollElement.getBoundingClientRect();
      if (lineLeft < (scrollLeft - 2) || lineLeft > (scrollLeft + scrollWidth + 2)) {
        this.hideDragLine();
        return;
      }
    }
    dragLine.style.top = top + UNIT_PX;
    dragLine.style.height = height + UNIT_PX;
    dragLine.style.left = lineLeft + UNIT_PX;
    dragLine.style.display = 'block';
  }
}

export default ReactDragColumnView;
