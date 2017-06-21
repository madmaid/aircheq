"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const superagent_1 = require("superagent");
class Program {
    constructor(id, service, channel, title, info, start, end, duration, isMovie, isRepeat, isReserved) {
        this.id = id;
        this.service = service;
        this.channel = channel;
        this.title = title;
        this.info = info;
        this.start = start;
        this.end = end;
        this.duration = duration;
        this.isMovie = isMovie;
        this.isRepeat = isRepeat;
        this.isReserved = isReserved;
    }
}
exports.Program = Program;
function jsonToProgram(jsonobj) {
    const start = new Date(jsonobj.start);
    const end = new Date(jsonobj.end);
    const duration = end.getDate() - start.getDate();
    return new Program(jsonobj.id, jsonobj.service, jsonobj.channel || '', jsonobj.title, jsonobj.info, start, end, duration, jsonobj.is_movie, jsonobj.is_repeat, jsonobj.is_reserved);
}
function fetchGuide() {
    const res = superagent_1.default.get('/api/programs.json')
        .then(res => { console.log(res); }, err => { console.log(err); });
    console.log(res);
    const guide = res.body.map(channel => {
        const programs = channel.programs.map(program => jsonToProgram(program));
        return {
            name: res.body.name,
            programs: programs
        };
    });
    return guide;
}
exports.fetchGuide = fetchGuide;
//# sourceMappingURL=program.js.map