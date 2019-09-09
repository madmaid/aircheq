import * as React from "react";
import styled from "styled-components";
import { defaultProps } from "recompose";

const Input = styled.input`
  flex: 1;
  min-width: 20px;
  margin: 0;
`;

const InputForm = styled.form`
  display: flex;
`;
const Button = styled.button`
  min-width: 10px;
`;

// TODO: type declaration
const SendButton: any = defaultProps({ type: "submit" })((props: any) => (
  <Button {...props} />
));

export { Input, InputForm, SendButton };
