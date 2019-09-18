import React, { useState } from "react";
import styled, { css } from "styled-components";
import { IRule } from "../stores/rule";
import { Modal, ModalAttr } from "./ModalUtil";
import ConfirmDialog from "./ConfirmDialog";

const StyledButton = styled.button``;

const _style = {
  content: css`
    top: "50%";
    left: "50%";
    right: "auto";
    bottom: "auto";
  `
};
const modalStyle = {
  content: {
    top: "50%",
    left: "50%",
    right: "auto",
    bottom: "auto",
    marginRight: "-50%",
    transform: "translate(-50%, -50%)"
  }
};
type Props = {
  rule: IRule;
  onAccept: Function;
};

function RuleDelete(props: Props) {
  const [isOpen, setIsOpen] = useState(false);
  return (
    <ModalAttr>
      <StyledButton onClick={() => setIsOpen(true)}>削除する</StyledButton>
      <Modal
        isOpen={isOpen}
        contentLabel={props.rule.id.toString()}
        onRequestClose={() => {
          setIsOpen(false);
        }}
        style={modalStyle}
      >
        <ConfirmDialog
          confirmation="本当に削除しますか？"
          close={() => setIsOpen(false)}
          yes={() => props.onAccept(props.rule.id)}
          no={() => {}}
        />
      </Modal>
    </ModalAttr>
  );
}

export default RuleDelete;
