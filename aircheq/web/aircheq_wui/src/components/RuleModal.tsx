import React from "react";
import {
  compose,
  withStateHandlers,
  StateHandlerMap,
  StateHandler,
  withHandlers
} from "recompose";

import RuleEditor from "./RuleEditor";
import { Modal, ModalAttr } from "./ModalUtil";

import OpenButton from "./buttons/OpenButton";
import CloseButton from "./buttons/CloseButton";

import { RuleProps } from "../stores/rule";

type HandlerInitProps = {
  initIsOpen: boolean;
};
type State = {
  isOpen: boolean;
};
type Updaters = StateHandlerMap<State> & {
  open: StateHandler<State>;
  close: StateHandler<State>;
};
type HandlerOuterProps = HandlerInitProps & State & Updaters;
//TODO: type declaration
const handleToggle: any = compose(
  withStateHandlers<State, Updaters, HandlerInitProps>(
    ({ initIsOpen = false }: HandlerInitProps) => ({
      isOpen: initIsOpen
    }),
    {
      open: () => () => ({
        isOpen: true
      }),
      close: () => () => ({
        isOpen: false
      })
    }
  )
);
type Props = RuleProps &
  HandlerOuterProps & {
    indication: string;
  };
const RuleModal: React.SFC<Props> = props => {
  const { rule, indication, send, isOpen, open, close } = props;
  return (
    <ModalAttr>
      <OpenButton onClick={open}>{indication}</OpenButton>
      <Modal
        isOpen={isOpen}
        contentLabel={rule.id == undefined ? "new" : rule.id.toString()}
        onRequestClose={close}
      >
        <RuleEditor rule={rule} send={send} closeModal={close} />
        <CloseButton onClick={close}>キャンセル</CloseButton>
      </Modal>
    </ModalAttr>
  );
};

export default handleToggle(RuleModal);
