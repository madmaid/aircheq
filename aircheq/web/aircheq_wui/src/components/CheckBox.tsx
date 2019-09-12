import React from "react";
import styled from "styled-components";

type HandlerProps = {
  onChange: (
    props: object
  ) => (event: React.ChangeEvent<HTMLInputElement>) => void;
};
type InnerProps = {
  name: string;
  checked: boolean;
};

const Input = styled.input`
  margin: 0;
`;
const CheckBox: React.SFC<InnerProps & HandlerProps> = ({
  name,
  checked,
  onChange
}) => (
  <Input type="checkbox" name={name} checked={checked} onChange={onChange} />
);

export default CheckBox;
