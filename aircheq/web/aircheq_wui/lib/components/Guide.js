"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const react_1 = require("react");
const styled_components_1 = require("styled-components");
const Program_1 = require("./Program");
const programStore = require("../stores/program");
const ProgramContainer = styled_components_1.default.li `
`;
const ProgramTitle = styled_components_1.default.div `
`;
const ProgramStart = styled_components_1.default.div `
`;
const Program = (props) => {
    return react_1.default.createElement(ProgramContainer, null,
        react_1.default.createElement(ProgramStart, null, props.program.start),
        react_1.default.createElement(ProgramTitle, null, props.program.title),
        react_1.default.createElement(Program_1.default, { program: props.program }));
};
const ProgramList = styled_components_1.default.ul `
`;
const ChannelContainer = styled_components_1.default.li `
`;
const ChannelName = styled_components_1.default.div `
`;
const Channel = (channel) => {
    return react_1.default.createElement(ChannelContainer, null,
        react_1.default.createElement(ChannelName, null, channel.name),
        react_1.default.createElement(ProgramList, null, channel.programs.map((p) => {
            return react_1.default.createElement(Program, { program: p });
        })));
};
const HourLabel = styled_components_1.default.div `
`;
const OneHourBase = styled_components_1.default.div `
`;
const OneHourContainer = (props) => {
    return react_1.default.createElement(OneHourBase, null,
        react_1.default.createElement(HourLabel, null, props.hour));
};
const HoursDivisionBase = styled_components_1.default.div `
`;
const HoursDivision = () => {
    const now = new Date().getHours();
    return react_1.default.createElement(HoursDivisionBase, null,
        () => {
            // 24hrs from now
            for (let i = now; i < 24; i++) {
                react_1.default.createElement(OneHourContainer, { hour: i });
            }
            for (let i = 0; i < 24 - now; i++) {
                react_1.default.createElement(OneHourContainer, { hour: i });
            }
        },
        ")}");
};
const Programs = styled_components_1.default.ul `
`;
const GuideContainer = styled_components_1.default.div `
`;
class Guide extends react_1.default.Component {
    compoenntDidMount() {
        const guide = programStore.fetchGuide();
        guide.forEach(channel => {
            this.channels.push(channel);
        });
    }
    render() {
        return react_1.default.createElement(GuideContainer, null,
            react_1.default.createElement(HoursDivision, null),
            react_1.default.createElement(Programs, null, this.channels.map(c => react_1.default.createElement(Channel, { name: c.name, programs: c.programs }))));
    }
}
exports.default = Guide;
//# sourceMappingURL=Guide.js.map