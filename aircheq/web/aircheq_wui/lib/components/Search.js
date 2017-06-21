"use strict";
var __decorate = (this && this.__decorate) || function (decorators, target, key, desc) {
    var c = arguments.length, r = c < 3 ? target : desc === null ? desc = Object.getOwnPropertyDescriptor(target, key) : desc, d;
    if (typeof Reflect === "object" && typeof Reflect.decorate === "function") r = Reflect.decorate(decorators, target, key, desc);
    else for (var i = decorators.length - 1; i >= 0; i--) if (d = decorators[i]) r = (c < 3 ? d(r) : c > 3 ? d(target, key, r) : d(target, key)) || r;
    return c > 3 && r && Object.defineProperty(target, key, r), r;
};
Object.defineProperty(exports, "__esModule", { value: true });
const react_1 = require("react");
const mobx_1 = require("mobx");
const mobx_react_1 = require("mobx-react");
const styled_components_1 = require("styled-components");
const superagent_1 = require("superagent");
const Input = styled_components_1.default.input `
`;
const SearchButton = styled_components_1.default.button `
`;
let SearchForm = class SearchForm extends react_1.default.Component {
    constructor() {
        super(...arguments);
        this.id = "";
        this.service = "";
        this.channel = "";
        this.title = "";
        this.info = "";
        this.search = () => {
            const query = {
                id: this.id,
                service: this.service,
                channel: this.channel,
                title: this.title,
                info: this.info,
            };
            const res = superagent_1.default.get('/api/search.json')
                .query(query)
                .then(res => { console.log(res); }, err => { console.log(err); });
        };
        this.handleKeyPress = (event) => {
            if (event.key === "enter") {
                this.search();
            }
        };
    }
    render() {
        return react_1.default.createElement("form", null,
            react_1.default.createElement(Input, { placeholder: "id", type: "text", value: this.id, onChange: e => { this.id = e.target.value; }, onKeyPress: this.handleKeyPress }),
            react_1.default.createElement(Input, { placeholder: "service", type: "text", value: this.service, onChange: e => { this.service = e.target.value; }, onKeyPress: this.handleKeyPress }),
            react_1.default.createElement(Input, { placeholder: "channel", type: "text", value: this.channel, onChange: e => { this.channel = e.target.value; }, onKeyPress: this.handleKeyPress }),
            react_1.default.createElement(Input, { placeholder: "title", type: "text", value: this.title, onChange: e => { this.title = e.target.value; }, onKeyPress: this.handleKeyPress }),
            react_1.default.createElement(Input, { placeholder: "info", type: "text", value: this.info, onChange: e => { this.info = e.target.value; }, onKeyPress: this.handleKeyPress }),
            react_1.default.createElement(SearchButton, { onClick: this.search }, "Search"));
    }
};
__decorate([
    mobx_1.observable
], SearchForm.prototype, "id", void 0);
__decorate([
    mobx_1.observable
], SearchForm.prototype, "service", void 0);
__decorate([
    mobx_1.observable
], SearchForm.prototype, "channel", void 0);
__decorate([
    mobx_1.observable
], SearchForm.prototype, "title", void 0);
__decorate([
    mobx_1.observable
], SearchForm.prototype, "info", void 0);
SearchForm = __decorate([
    mobx_react_1.observer
], SearchForm);
exports.default = SearchForm;
//# sourceMappingURL=Search.js.map