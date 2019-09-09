import "whatwg-fetch";
type IRule = {
  id: string | null;
  service: string;
  channel: string;
  title: string;
  info: string;

  repeat: boolean;
  encode: boolean;
};

type RuleProps = {
  rule: IRule;
  send: (rule: IRule) => void;
};

const initRuleState: IRule = {
  id: null,
  service: "",
  channel: "",
  title: "",
  info: "",

  repeat: true,
  encode: false
};

function jsonToRule<T extends IRule>(json: T): IRule {
  return json as IRule;
}
const validate = (rule: IRule) => {
  Object.keys(rule).forEach(k => (rule[k] = rule[k].trim()));
  return rule;
};
const fetchRules = () => fetch("/api/rules.json").then(res => res.json());

const postRule = (url: string, body: Object) => {
  fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(body)
  });
};
const sendNewRule = (rule: IRule) => {
  postRule("/api/add_rule.json", rule);
};
const sendEdited = (rule: IRule) => {
  postRule("/api/change_rule.json", rule);
};
const deleteRule = (id: Number) => {
  postRule("/api/delete_rule.json", { id });
};
export {
  IRule,
  //  Rule,
  RuleProps,
  initRuleState,
  jsonToRule,
  fetchRules,
  sendNewRule,
  sendEdited,
  deleteRule
};
