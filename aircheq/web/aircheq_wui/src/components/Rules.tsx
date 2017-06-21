import * as React from "react"
import styled from "styled-components"

import "whatwg-fetch"

import { Modal, OpenButton, CloseButton } from "./ModalUtil"
import { Input, InputForm, SendButton } from "./FormUtil"
import { IRule, Rule, jsonToRule } from "../stores/rule"


interface RuleProps {
    send: Function
    rule?: Rule,
}

const CheckBox = styled.input`
    margin: 0;
`
const ButtonContainer = styled.div`
`
const RuleForm = InputForm.extend`
    flex-direction: column;
`
const RuleInput = Input.extend`
    margin: 0;
`
interface RuleEditProps extends RuleProps {
    closeModal: Function
}

class RuleEdit extends React.Component <RuleEditProps, IRule> {
    constructor(props: RuleEditProps) {
        super(props)
        if (this.props.rule === undefined){
            this.state = {
                id: undefined,
                service: "",
                channel: "",
                title: "",
                info: "",

                repeat: true,
                encode: false, 
            }
        } else {
            this.state = this.props.rule
        }

    }
    send() {
        this.props.send(this.state)
        this.props.closeModal()
    }
    private onKeyPress(event: any) {
        if(event.key === "enter"){
            this.send()
        }
    }
    private onCheckChange(event: any) {
        const target = event.currentTarget
        this.setState({ [target.name]: target.checked })
    }
    render() {
        return <RuleForm>
                    <RuleInput placeholder="service" type="text"
                           value={this.state.service}
                           onChange={ e => {
                               this.setState({ service: e.currentTarget.value })
                               }}
                           onKeyPress={this.onKeyPress}
                    />
                    <RuleInput placeholder="channel" type="text"
                           value={this.state.channel}
                           onChange={ e => {
                               this.setState({ channel: e.currentTarget.value })
                           }}
                           onKeyPress={this.onKeyPress}
                    />
                    <RuleInput placeholder="title" type="text"
                           value={this.state.title}
                           onChange={ e => {
                               this.setState({ title: e.currentTarget.value })
                               }}
                           onKeyPress={this.onKeyPress}
                    />
                    <RuleInput placeholder="info" type="text"
                           value={this.state.info}
                           onChange={ e => {
                               this.setState({ info: e.currentTarget.value })
                           }}
                           onKeyPress={this.onKeyPress}
                    />
                    <CheckBox type="checkbox"
                              name="repeat"
                              checked={this.state.repeat}
                              onChange={e => this.onCheckChange(e)}
                    />再放送を含める

                    <CheckBox type="checkbox"
                              name="encode"
                              checked={this.state.encode}
                              onChange={e => this.onCheckChange(e)}
                    />エンコードする
                    <ButtonContainer>

                    <SendButton type="button" onClick={() => {
                        this.send()
                    }}>送信</SendButton>

                    </ButtonContainer>
                </RuleForm>
    }
}
interface ModalState {
    modal: boolean
}

interface RuleModalProps extends RuleProps {
    openButtonIndication: string,
    refresh: Function
}
class RuleModal extends React.Component <RuleModalProps, ModalState> {
    constructor(props: RuleModalProps) {
        super(props)
        this.state = { modal: false }
    }
    openModal() {
        this.setState({ modal: true })
    }
    closeModal() {
        this.setState({ modal: false })
        this.props.refresh()
    }
    render() {
        return <RuleAttr>
                <OpenButton onClick={() => {this.openModal()}}>
                    { this.props.openButtonIndication }
                </OpenButton>
                <Modal isOpen={this.state.modal}
                    contentLabel={this.props.rule ? this.props.rule.id.toString() : "new" }
                    onRequestClose={() => {this.closeModal()}}
                >
                    <RuleEdit rule={this.props.rule}
                              send={this.props.send}
                              closeModal={() => this.closeModal()}
                    />
                    <CloseButton onClick={(e) => {
                        this.closeModal()
                    }}>キャンセル
                    </CloseButton>
                </Modal>

               </RuleAttr>
    }
}

interface RulesState {
    rules: Rule[] 
}
const RuleList = styled.ul`
    margin: 0;
    padding: 0;
`
const RuleContainer = styled.li`
    list-style-type: none;
    display: flex;
    margin-top: 5px;
    margin-bottom: 5px;
    text-align: center;
`
const _RuleAttr = styled.div`
    margin-left: 5px;
    margin-right: 5px;
`
const RuleAttr = _RuleAttr.extend`
    flex: 1;
`
const RuleId = _RuleAttr.extend`
    width: 20px;
`

const RuleIndexContainer = styled.div`
    list-style-type: none;
    display: flex;
    margin-top: 5px;
    margin-bottom: 5px;
    padding: 0;
`
const _RuleIndex = _RuleAttr.extend`
    color: white;
    background: #60bde5;
    text-align: center;
`
const RuleIndex = _RuleIndex.extend`
    flex: 1;
`
const RuleIndexId = _RuleIndex.extend`
    width: 20px;
`
const RulesContainer = styled.div`
    padding: 0;
    margin: 0;
`
class Rules extends React.Component <{}, RulesState> {
    render() {
        return  <RulesContainer>
                <RuleIndexContainer>
                    <RuleIndexId>id</RuleIndexId>
                    <RuleIndex>service</RuleIndex>
                    <RuleIndex>channel</RuleIndex>
                    <RuleIndex>title</RuleIndex>
                    <RuleIndex>info</RuleIndex>
                    <RuleIndex>encode</RuleIndex>
                    <RuleIndex>repeat</RuleIndex>
                    <RuleIndex>Open Editor</RuleIndex>
                </RuleIndexContainer>
                <RuleList>
                {(() => this.state.rules.map((rule, i) => 
                    <RuleContainer key={i}>
                        <RuleId>{ rule.id }</RuleId>
                        <RuleAttr>{ rule.service }</RuleAttr>
                        <RuleAttr>{ rule.channel }</RuleAttr>
                        <RuleAttr>{ rule.title }</RuleAttr>
                        <RuleAttr>{ rule.info }</RuleAttr>
                        <RuleAttr>{ rule.encode ? "する" : "しない" }</RuleAttr>
                        <RuleAttr>{ rule.repeat ? "含む" : "" }</RuleAttr>
                        <RuleModal rule={rule}
                                   send={this.sendEdited}
                                   refresh={() => { this.fetch() }}
                                   openButtonIndication={"編集する"}
                        />
                    </RuleContainer>
                ))()}
                </RuleList>
                <RuleModal send={this.sendNewRule}
                           refresh={() => { this.fetch() }}
                           openButtonIndication={"新しいルールを作成する"}
                />
                </RulesContainer>
    }
    constructor(){
        super()
        this.state = { rules: [] }
    }
    componentDidMount() {
        this.fetch()
    }
    fetch(){
        fetch("/api/rules.json")
                .then(res => res.json())
                .then(( json )=> {
                    this.setState({ rules: json.map((r: any) => jsonToRule(r)) })
                })
    }
    sendNewRule(rule: IRule){
        fetch("/api/add_rule.json", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(rule)
        })
    }
    sendEdited(rule: IRule){
        fetch("/api/change_rule.json", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(rule)
        })
    }
}
export default Rules