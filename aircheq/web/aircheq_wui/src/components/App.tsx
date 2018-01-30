import * as React from 'react'
import {
    BrowserRouter as _Router,
    Route,
    Link,
} from "react-router-dom"
import styled from "styled-components"

import Home from "./Home"
import Guide from "./Guide"
import Rules from "./Rules"
import SearchForm from "./Search"
import Detail, { DetailProps } from "./ProgramDetail"

const Sidebar = styled.ul`
    display: flex;
    background: grey;
    position: fixed;
    margin: 0;
    top: 0;
    width: 100%;
`

const Contents = styled.div`
    background: white;
    position: block;
    margin-top: 50px;
`
const AppContainer = styled.div`
`

interface IRoute {
    path: string,
    exact: boolean,
    content: Function,
    sidebar?: {
        title: string
    },
}


const routes: IRoute[] = [
    {
        path: '/',
        exact: true,
        content: () => <Home/>,
        sidebar: {
            title: "Home",
        },
    },
    {
        path: '/guide',
        exact: false,
        content: () => <Guide/>,
        sidebar: {
            title: "Guide",
        }
    },
    {
        path: '/rules',
        exact: false,
        content: () => <Rules/>,
        sidebar: {
            title: "Rules",
        }
    },
    {
        path: '/search',
        exact: false,
        content: () => <SearchForm />,
        sidebar: {
            title: "Search",
        }
    },
    {
        path: '/program/:id',
        exact: false,
        content: (props: DetailProps) => {
            if (props.match !== undefined){
                return <Detail id={props.match.params.id} />
            }
        }
    },
]

const LinkContainer = styled.li`
    list-style-type: none;
    flex: 1;
    &.${(props: any) => props.activeClassName} {
        background-color: paleturquoise;
    }
`
const ContentLink = styled(Link)`
    color: white;
    text-decoration: none;
`
const Router = styled(_Router)`
`

const App = () =>
<Router>
    <AppContainer>
        <Sidebar>
        {(() => routes.map((route, i) => {
                if (route.sidebar !== undefined) {
                    return <LinkContainer key={i}>
                                <ContentLink to={route.path}>
                                {route.sidebar.title}
                                </ContentLink>
                        </LinkContainer>
                }
            })
        )()}
        </Sidebar>


        <Contents>
        {(() => routes.map((route, i) =>
                <Route key={i}
                    exact={route.exact}
                    path={route.path}
                    render={route.content as any}
                />
            )
        )()}
        </Contents>
    </AppContainer>
</Router>

export default App