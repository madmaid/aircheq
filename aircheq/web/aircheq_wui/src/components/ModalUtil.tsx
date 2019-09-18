import React from "react";
import styled from "styled-components";
import ReactModal from "react-modal";

const ModalAttr = styled.div`
  margin-left: 5px;
  margin-right: 5px;
  flex: 1;
`;
const Modal: React.SFC<ReactModal.Props> = props => {
  const defaultBGColor = "rgba(0, 0, 0, 0.75)";
  const defaultOverlay = {
    backgroundColor: defaultBGColor
  };
  const defaultStyle = {
    overlay: defaultOverlay
  };

  // override transparency
  let _style = props.style;
  if (_style == undefined) {
    _style = defaultStyle;
  } else if (_style.overlay == undefined) {
    _style.overlay = defaultOverlay;
  } else if (_style.overlay.backgroundColor == undefined) {
    _style.overlay.backgroundColor = defaultBGColor;
  }

  return <ReactModal {...props} style={_style} />;
};
export { Modal, ModalAttr };
