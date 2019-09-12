import React from "react";
import { compose, withState, withHandlers, ComponentEnhancer } from "recompose";

import { Input, InputForm, SendButton } from "./FormUtil";
import CheckBox from "./CheckBox";

import { IRule, RuleProps, initRuleState } from "../stores/rule";

const RuleForm = InputForm.extend`
  flex-direction: column;
`;

const handleKeyPress: any = withHandlers({
  onKeyPress: (props: any) => (event: any) => {
    if (event.key === "enter") {
      props.send(props.rule);
    }
  }
});
type RuleInputProps = {
  rule: IRule;
  name: string;
  onChange: (event: React.FormEvent<HTMLInputElement>) => void;
};
const RuleInput: React.SFC<RuleInputProps> = ({ name, rule, onChange }) => (
  <Input
    name={name}
    placeholder={name}
    type="text"
    value={rule[name]}
    onChange={onChange}
  />
);

type Props = RuleProps & {
  localRule: IRule;
  closeModal: Function;
  onChange: (props: any) => (event: React.FormEvent<HTMLInputElement>) => void;
};
const editablize = compose(
  withState("localRule", "updateValue", (props: Props) => props.rule),
  withHandlers({
    onChange: (props: any) => (event: React.FormEvent<HTMLInputElement>) => {
      const target = event.currentTarget;
      const value = target.type === "checkbox" ? target.checked : target.value;

      props.updateValue((state: IRule) => ({
        ...state,
        [target.name]: value
      }));
    }
  })
);

const RuleEditor: React.SFC<Props> = props => {
  const { onChange, localRule, send, closeModal } = props;
  return (
    <RuleForm>
      <RuleInput name="service" rule={localRule} onChange={onChange} />
      <RuleInput name="channel" rule={localRule} onChange={onChange} />
      <RuleInput name="title" rule={localRule} onChange={onChange} />
      <RuleInput name="info" rule={localRule} onChange={onChange} />
      <CheckBox name="repeat" checked={localRule.repeat} onChange={onChange} />
      再放送を含める
      <CheckBox name="encode" checked={localRule.encode} onChange={onChange} />
      エンコードする
      <SendButton
        onClick={() => {
          send(localRule);
          closeModal();
        }}
      >
        送信
      </SendButton>
    </RuleForm>
  );
};
const enhance: ComponentEnhancer<any, any> = compose(
  handleKeyPress,
  editablize
);
export default enhance(RuleEditor);
