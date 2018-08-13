import * as React from "react";
import { compose, withStateHandlers, mapProps, lifecycle } from "recompose";
import styled from "styled-components";

import RuleModal from "./RuleModal";

import {
  IRule,
  initRuleState,
  RuleProps,
  jsonToRule,
  fetchRules,
  sendNewRule,
  sendEdited,
  sendDelete
} from "../stores/rule";

const RuleList = styled.ul`
  margin: 0;
  padding: 0;
`;
const RuleContainer = styled.li`
  list-style-type: none;
  display: flex;
  margin-top: 5px;
  margin-bottom: 5px;
  text-align: center;
`;
const _RuleAttr = styled.div`
  margin-left: 5px;
  margin-right: 5px;
`;
const RuleAttr = _RuleAttr.extend`
    flex: 1;
`;
const RuleId = _RuleAttr.extend`
    width: 20px;
`;

const RuleIndexContainer = styled.div`
  list-style-type: none;
  display: flex;
  margin-top: 5px;
  margin-bottom: 5px;
  padding: 0;
`;
const _RuleIndex = _RuleAttr.extend`
    color: white;
    background: #60bde5;
    text-align: center;
`;
const RuleIndex = _RuleIndex.extend`
    flex: 1;
`;
const RuleIndexId = _RuleIndex.extend`
    width: 20px;
`;
const RulesContainer = styled.div`
  padding: 0;
  margin: 0;
`;
const RuleIndices = () => (
  <RuleIndexContainer>
    <RuleIndexId>id</RuleIndexId>
    <RuleIndex>service</RuleIndex>
    <RuleIndex>channel</RuleIndex>
    <RuleIndex>title</RuleIndex>
    <RuleIndex>info</RuleIndex>
    <RuleIndex>encode</RuleIndex>
    <RuleIndex>repeat</RuleIndex>
    <RuleIndex>Open Editor</RuleIndex>
  </RuleIndexContainer>
);

type Props = RuleProps & {
  index: number;
};
const RuleItem = ({ index, rule, send }: Props) => (
  <RuleContainer key={index}>
    <RuleId>{rule.id}</RuleId>
    <RuleAttr>{rule.service}</RuleAttr>
    <RuleAttr>{rule.channel}</RuleAttr>
    <RuleAttr>{rule.title}</RuleAttr>
    <RuleAttr>{rule.info}</RuleAttr>
    <RuleAttr>{rule.encode ? "する" : "しない"}</RuleAttr>
    <RuleAttr>{rule.repeat ? "含む" : ""}</RuleAttr>
    <RuleModal rule={rule} send={send} indication={"編集する"} />
  </RuleContainer>
);
const initialFetch: any = compose(
  withStateHandlers<{ rules: IRule[] }, any, any>(
    {
      rules: []
    },
    {
      setRules: () => (data: IRule[]) => ({
        rules: data
      })
    }
  ),
  lifecycle({
    componentWillMount() {
      fetchRules()
        .then(json => json.map((r: IRule) => jsonToRule(r)))
        .then((this as any).props.setRules);
    }
  })
);

const Rules = (props: any) => (
  <RulesContainer>
    <RuleIndices />
    <RuleList>
      {(() =>
        //FIXME: index should be unique
        props.rules.map((rule: IRule, i: number) => (
          <RuleItem index={i} rule={rule} send={sendEdited} />
        )))()}
    </RuleList>
    <RuleModal
      rule={initRuleState}
      send={sendNewRule}
      indication={"新しいルールを作成する"}
    />
  </RulesContainer>
);
export default initialFetch(Rules);
