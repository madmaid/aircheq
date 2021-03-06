import "whatwg-fetch";
type INewRule = {
  service: string;
  channel: string;
  title: string;
  info: string;

  repeat: boolean;
  encode: boolean;
};

type IRule = INewRule & {
  id: number;
};

type RuleProps = {
  rule: IRule;
  send: (rule: IRule) => void;
};

const initRuleState: INewRule = {
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

const postRule = (url: string, body: Object) =>
  fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(body)
  }).then(res => res.json());

const sendNewRule = (rule: INewRule) =>
  postRule("/api/add_rule.json", rule).then(json_ => json_.map(jsonToRule));

const sendEdited = (rule: IRule) => postRule("/api/change_rule.json", rule);

const deleteRule = (id: Number) => postRule("/api/delete_rule.json", { id });
export {
  IRule,
  INewRule,
  RuleProps,
  initRuleState,
  jsonToRule,
  fetchRules,
  sendNewRule,
  sendEdited,
  deleteRule
};
