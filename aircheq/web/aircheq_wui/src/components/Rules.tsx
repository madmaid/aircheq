import React, { useState, useEffect } from "react";
import styled from "styled-components";

import RuleModal from "./RuleModal";
import RuleDelete from "./RuleDelete";

import {
  IRule,
  INewRule,
  initRuleState,
  RuleProps,
  jsonToRule,
  fetchRules,
  sendNewRule,
  sendEdited,
  deleteRule
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
    <RuleIndex>Delete</RuleIndex>
  </RuleIndexContainer>
);

type ItemProps = RuleProps & {
  index: number | string;
  del: (id: Number) => void;
};
const RuleItem = ({ index, rule, send, del }: ItemProps) => (
  <RuleContainer key={index}>
    <RuleId>{rule.id}</RuleId>
    <RuleAttr>{rule.service}</RuleAttr>
    <RuleAttr>{rule.channel}</RuleAttr>
    <RuleAttr>{rule.title}</RuleAttr>
    <RuleAttr>{rule.info}</RuleAttr>
    <RuleAttr>{rule.encode ? "する" : "しない"}</RuleAttr>
    <RuleAttr>{rule.repeat ? "含む" : ""}</RuleAttr>
    <RuleModal rule={rule} send={send} indication={"編集する"} />
    <RuleDelete rule={rule} onAccept={del} />
  </RuleContainer>
);

function Rules() {
  const [rules, setRules] = useState([]);
  const _fetchRules = () => {
    fetchRules().then(rs => {
      setRules(rs);
    });
  };
  useEffect(() => {
    _fetchRules();
  }, []);
  return (
    <RulesContainer>
      <RuleIndices />
      <RuleList>
        {(() =>
          rules.map((rule: IRule, i: number) => (
            <RuleItem
              index={"rule-item-" + i}
              rule={rule}
              send={(rule: IRule) => sendEdited(rule).then(setRules)}
              del={(id: Number) => deleteRule(id).then(setRules)}
            />
          )))()}
      </RuleList>
      <RuleModal
        rule={initRuleState}
        send={(rule: INewRule) => sendNewRule(rule).then(setRules)}
        indication={"新しいルールを作成する"}
      />
    </RulesContainer>
  );
}
export default Rules;
