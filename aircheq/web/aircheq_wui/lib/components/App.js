"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const react_1 = require("react");
const react_router_dom_1 = require("react-router-dom");
const styled_components_1 = require("styled-components");
const Guide_1 = require("./Guide");
const HomeContainer = styled_components_1.default.div `
`;
const Home = () => {
    react_1.default.createElement(HomeContainer, null, "Home");
};
const ContentsContainer = styled_components_1.default.ul `
`;
const Content = styled_components_1.default(react_router_dom_1.Link) `
`;
const routes = [
    {
        path: '/',
        exact: true,
        content: () => react_1.default.createElement(Home, null)
    },
    {
        path: '/guide',
        content: () => react_1.default.createElement(Guide_1.default, null)
    },
];
const App = () => {
    return react_1.default.createElement(react_router_dom_1.BrowserRouter, null,
        react_1.default.createElement("div", null,
            react_1.default.createElement(ContentsContainer, null,
                react_1.default.createElement("li", null,
                    react_1.default.createElement(Content, { to: "/" }, "Home\uD83C\uDFE0")),
                react_1.default.createElement("li", null,
                    react_1.default.createElement(Content, { to: "/guide" }, "Guide\uD83D\uDCC5")),
                react_1.default.createElement("li", null,
                    react_1.default.createElement(Content, { to: "/reserved" }, "Reserved\u2713"))),
            routes.map((route, i) => {
                react_1.default.createElement(react_router_dom_1.Route, { key: i, path: route.path, exact: route.exact, component: route.content });
            })));
};
exports.default = App;
//# sourceMappingURL=App.js.map