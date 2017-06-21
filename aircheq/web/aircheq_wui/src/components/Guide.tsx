import * as React from "react"
import styled from "styled-components"

import * as moment from "moment"

import { DetailLink } from "./ProgramDetail"
import * as model from "../stores/program"

const ProgramStart = styled.div`
    margin: 1px 0;
    padding: 1px 0;
    font-size: 12px;
`
const ProgramTitle = styled.div`
    margin: 0;
    padding: 0;
    font-size: 14px;
`

const ProgramContainer = styled.li`
    background-color: #eeeeee;
    border-top: solid 1px white ;
    display: flex;

    overflow: hidden;
`

interface ProgramProps {
    program: model.Program,
    key: number,
}

const Program = (props: ProgramProps) => {
    const { key, program } = props
    const duration = program.duration || program.start.diff(program.end)
    const now = moment()

    let height: moment.Duration

    if ( program.start.isBefore(now) ) {
        const diffFromNow = moment.duration(now.diff(program.start))
        height = duration.subtract(diffFromNow)
    } else {
        height = duration
    }

    const styles = {
        "height": String(height.asMinutes() * 3 - 1) + "px",
    }
    return  <ProgramContainer style={styles} key={key}>
                <ProgramStart>{program.start.format("HH:mm")}</ProgramStart>
                <ProgramTitle>
                    <DetailLink to={"/program/" + program.id.toString()}>
                    {program.title}
                    </DetailLink>
                </ProgramTitle>
            </ProgramContainer>

}

const ChannelContainer = styled.li`
    flex: 1;
    min-width: 160px;
    margin-left: 5px;
    margin-right: 5px;
`
const ChannelName = styled.div`
    color: white;
    background: #60bde5;
    text-align: center;
    /*
    TODO
    position: absolute;
    */
`
const ProgramsList = styled.ul`


    list-style-type: none;
    padding-left: 0;
`
interface ChannelProps extends model.Channel {
    key: number
}
const Channel = ( props: ChannelProps ) =>
<ChannelContainer key={props.key}>
    <ChannelName>{props.nameJP}</ChannelName>
    <ProgramsList>
    {(() => props.programs.map((p, i) =>
                <Program program={p} key={i}/>
            )
    )()}
    </ProgramsList>
</ChannelContainer>

const HourLabel = styled.div`
`
const OneHourBase = styled.div`
`

const OneHourContainer = (props: { hour: number }) =>
<HourLabel>{props.hour}</HourLabel>

const HoursDivisionBase = styled.div`
`
const HoursDivision = () => {
    const now = moment().hours()
    return <HoursDivisionBase>
            {(() => {
                let division = []
                // 24hrs from now
                for (let i = now; i < 24; i++) {
                    division.push(<OneHourContainer hour={i} />)
                }
                for (let i = 0; i < now; i++) {
                    division.push(<OneHourContainer hour={i} />)
                }
                return division.map((oneHour, i) => 
                        <OneHourBase key={i}>
                            {oneHour}
                        </OneHourBase>
                    )
            })()}
            </HoursDivisionBase>
}

const ChannelList= styled.ul`
    list-style-type: none;
    list-style-position: inside;
    display: flex;
`
const GuideContainer = styled.div`
`

interface GuideState {
    channels: model.Channel[]
}

class Guide extends React.Component <{}, GuideState> {
    state: GuideState
    constructor() {
        super()
        this.state = {channels: []}
    }
    render() {
        return  <GuideContainer>
                <ChannelList>
                {(() => this.state.channels.map((c, i) => 
                        <Channel name={c.name} nameJP={c.nameJP} programs={c.programs} key={i}/>
                    )
                )()}
                </ChannelList>
                </GuideContainer>
    }
    componentDidMount() {
        model.fetchGuide()
            .then(( guide: model.Channel[] ) => {
                this.setState({ channels: guide })
            })
    }
}
export default Guide