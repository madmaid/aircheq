"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const react_1 = require("react");
const styled_components_1 = require("styled-components");
const react_modal_1 = require("react-modal");
const superagent_1 = require("superagent");
const ProgramAttr = styled_components_1.default.div `
`;
const ProgramContainer = styled_components_1.default.div `
`;
const ReserveButton = styled_components_1.default.button `
`;
class Detail extends react_1.default.Component {
    constructor(props) {
        super(props);
        this.reserve = (programId) => {
            superagent_1.default.post("/api/reserve.json")
                .send({ id: programId })
                .end();
        };
    }
    render() {
        const program = this.props.program;
        return react_1.default.createElement(ProgramContainer, null,
            react_1.default.createElement(ProgramAttr, null, program.channel),
            react_1.default.createElement(ProgramAttr, null, program.start),
            react_1.default.createElement(ProgramAttr, null, program.title),
            react_1.default.createElement(ProgramAttr, null, program.info),
            react_1.default.createElement(ReserveButton, { onClick: () => this.reserve(program.id) }, "Reserve"));
    }
}
const ProgramDetail = (props) => {
    return react_1.default.createElement(react_modal_1.default, { isOpen: false },
        react_1.default.createElement(Detail, { program: props.program }));
};
exports.default = ProgramDetail;
//# sourceMappingURL=Program.js.map