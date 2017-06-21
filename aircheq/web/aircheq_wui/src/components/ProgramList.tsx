import * as React from "react"
import * as moment from "moment"
import styled from "styled-components"

const ProgList = styled.ul`
    padding: 0;
    margin: 0;
    list-style-type: none;
    list-style-position: inside;
    flex-flow: row wrap;
`
const ProgContainer = styled.li`
    background-color: #eeeeee;
    margin-bottom: 5px;
    margin-top: 5px;
    display: block;
`
const ProgService = styled.div`
`
const ProgChannel = styled.div`
`
const ProgTime = styled.div`
`
const ProgDuration = styled.div`
`
const ProgReserved = styled.div`
    color: red;
`

export {
    ProgList,
    ProgContainer,
    ProgService,
    ProgChannel,
    ProgTime,
    ProgDuration,
    ProgReserved,
}