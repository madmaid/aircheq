import * as React from "react"
import { match as Match, Link } from "react-router-dom"
import styled from "styled-components"

import * as moment from "moment"
import "whatwg-fetch"

import * as model from "../stores/program"
import { ProgReserved } from "./ProgramList"

const ProgramAttr = styled.div`
`
const ProgramTitle = styled.div`
    font-size: 20px;
    color: white;
    background: #60bde5;
`
const ProgramTime = styled.div`
`
const ProgramContainer = styled.div`
`
const ReserveButton = styled.button`
`
const DetailLink = styled(Link)`
    margin: 0;
    padding: 0;
    text-decoration: none;
`

interface DetailParams {
    id: number 
}
interface DetailProps {
    match?: Match<DetailParams>
}
interface DetailState {
    program: model.IProgram
}

class Detail extends React.Component <DetailParams, DetailState> {
    constructor(props: DetailParams) {
        super(props)

        this.state = {
            program: {
                id: 0,
                service: "",
                channel: "",
                channelJP: "",
                title: "",
                info: "",
                start: moment.min(),
                end: moment.min(),
                duration: moment.duration(),
                isRepeat: false,
                isMovie: false,
                isReserved: false,
                isRecorded: false,
            }
        }
    }
    componentDidMount() {
        this.setProgram()
    }
    setProgram(){
        this.fetchProgram(this.props.id)
            .then(program => {
                this.setState({program: program})
            })
    }
    fetchProgram(programId: number){
        return fetch("/api/program_by_id.json", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ id: programId })
        }).then(res => res.json())
          .then(json => model.jsonToProgram(json))

    }
    reserve(programId: number){
        fetch("/api/reserve.json", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ id: programId })
        }).then(() => {
            this.setProgram()
        })
    }
    render() {
        const { program } = this.state
        const start = program.start.locale("ja").format("LLL")
        const endFormatter = program.start.isSame(program.end, "day") ? "LT" : "LLL"
        const end = program.end.locale("ja").format(endFormatter)
        const duration = program.duration.asMinutes()
        const time = `${start} - ${end} (${duration}分間)`

        return <ProgramContainer>
                    <ProgramTitle>{program.title}</ProgramTitle>
                    <ProgReserved>{program.isReserved ? "予約済" : ""}</ProgReserved>
                    <ProgReserved>{program.isRecorded ? "録音済" : ""}</ProgReserved>
                    <ProgramTime>{time}</ProgramTime>
                    <ProgramAttr>Service : {program.service}</ProgramAttr>
                    <ProgramAttr>チャンネル名 : {program.channelJP}</ProgramAttr>
                    <br/>
                    <ProgramAttr>{program.info}</ProgramAttr>
                    
                    <ReserveButton onClick={(e) => {
                        e.preventDefault()
                        this.reserve(program.id)
                    }}>{ program.isReserved ? "この番組の予約を解除する" : "この番組を手動予約する" }
                    </ReserveButton>
                </ProgramContainer>
    }
}

export {
    DetailLink,
    DetailProps,
    Detail as default
}