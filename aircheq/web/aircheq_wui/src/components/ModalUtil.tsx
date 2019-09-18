import React from "react";
import styled from "styled-components";
import ReactModal from "react-modal";

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
const OpenButton = styled.button``;
const CloseButton = styled.button`
  position: absolute;
  right: 20px;
  bottom: 20px;
`;
export { Modal, OpenButton, CloseButton };
