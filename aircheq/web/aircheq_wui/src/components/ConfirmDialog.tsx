import React from "react";
import styled from "styled-components";

import YesButton from "./buttons/YesButton";
import NoButton from "./buttons/NoButton";

type Props = {
  confirmation: string;
  close: Function;
  yes: Function;
  no: Function;
};
const closeAfterDone = (f: Function, close: Function) => () => {
  f();
  close();
};

const DialogContainer = styled.div`
  display: grid;
  grid-template-rows: 1fr 2fr 6fr 1fr 0%;
  grid-template-columns: 1% repeat(2, 1fr) 2fr repeat(2, 1fr) 1%;
`;

const Confirmation = styled.p`
  grid-row: 2;
  grid-column: 4/5;
  text-align: center;

  font-weight: bold;
  font-size: x-large;
`;

const Target = styled.p`
  grid-row: 3;
  grid-column: 4/5;
  text-align: center;
`;

function ConfirmDialog(props: Props) {
  let { yes, no, close } = props;
  return (
    <DialogContainer>
      <Confirmation>{props.confirmation}</Confirmation>
      <YesButton type="submit" onClick={closeAfterDone(yes, close)}>
        実行
      </YesButton>
      <NoButton onClick={closeAfterDone(no, close)}>キャンセル</NoButton>
    </DialogContainer>
  );
}
export default ConfirmDialog;
