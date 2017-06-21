interface IRule {
        id?: string,
        service: string,
        channel: string,
        title: string,
        info: string,

        repeat: boolean,
        encode: boolean, 
}
class Rule implements IRule {
    constructor(
        readonly id: string,
        readonly service: string,
        readonly channel: string,
        readonly title: string,
        readonly info: string,

        readonly repeat: boolean,
        readonly encode: boolean
    ){}
}
function jsonToRule(json: any){
    return new Rule(
        json.id,
        json.service,
        json.channel,
        json.title,
        json.info,

        json.repeat,
        json.encode
    )
}

export {
    IRule,
    Rule,
    jsonToRule
}