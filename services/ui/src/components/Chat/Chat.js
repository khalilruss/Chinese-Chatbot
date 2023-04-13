import './Chat.css'
import 'react-chatbox-component/dist/style.css';
import React, { useState, useEffect, useRef } from "react";
import { ChatBox } from 'react-chatbox-component';
import inMemoryJWT from '../../utils/inMemoryJWT'
import CHATBOT_AVATAR from '../../assets/chatbot.svg'
import USER_AVATAR from '../../assets/user-avatar.svg'
import { postClassify, postExtract } from '../../utils/api-client'
import paginationFactory from 'react-bootstrap-table2-paginator';
import 'react-bootstrap-table2-paginator/dist/react-bootstrap-table2-paginator.min.css';
import BootstrapTable from 'react-bootstrap-table-next';

const Chat = () => {
  const [messageHistory, setMessageHistory] = useState([])
  const [wordClassifications, setWordClassifications] = useState([])
  const [grammarRules, setGrammarRules] = useState([])
  const [loading, setLoading] = useState(true)
  const [averageWordLevel, setAverageWordLevel] = useState(0)
  const [averageGrammarLevel, setAverageGrammarLevel] = useState(0)
  const currnetUser = {
    "uid": "user1"
  }
  const ws = useRef(null);
  const msgRef = useRef([])

  const columnsWord = [{
    dataField: 'word',
    text: 'Word'
  }, {
    dataField: 'level',
    text: 'Level'
  }];

  const columnsGrammar = [{
    dataField: 'rule',
    text: 'Grammar Pattern'
  }, {
    dataField: 'level',
    text: 'Level',
    sort: true
  }];
  useEffect(() => { msgRef.current = messageHistory }, [messageHistory])

  useEffect(() => {
    let isMounted = true;
    if (isMounted) {
      let token = inMemoryJWT.getToken()
      ws.current = new WebSocket(`ws://localhost:8005/chat?token=${token}`);
      ws.current.onopen = () => {
        setLoading(false)
        console.log("websocket is connected");
      };
      ws.current.onclose = e => {
        let botMsg = createFullMessage('聊天结束了 (Chat Ended)', 'chatbot', 'chatbot1', CHATBOT_AVATAR)
        updateMessages(botMsg)
        console.log('websocket is closed.');
      }
      ws.current.onmessage = e => {
        let botMsg = createFullMessage(e.data, 'chatbot', 'chatbot1', CHATBOT_AVATAR)
        updateMessages(botMsg)
      };
    }
    return () => { isMounted = false; ws.current.close() };

  }, [])

  useEffect(() => {
    setAverageWordLevel(calcAverage(wordClassifications))
  }, [wordClassifications])

  useEffect(() => {
    setAverageGrammarLevel(calcAverage(grammarRules))
  }, [grammarRules])

  const calcAverage = array => {
    let sum = 0;
    if (array.length === 0) {
      return sum;
    }
    array.forEach(item => {
      sum += item.level
    })
    let average = sum / array.length
    return Math.round(average * 100) / 100;
  }

  const removeDuplicates = array => {
    const seen = new Set();
    return array.filter(el => {
      if (el.hasOwnProperty('word')) {
        const duplicate = seen.has(el.word);
        seen.add(el.word);
        return !duplicate;
      } else {
        const duplicate = seen.has(el.rule);
        seen.add(el.rule);
        return !duplicate;
      }
    });
  }

  const createFullMessage = (text, name, uid, avatar) => {
    return {
      "text": text,
      "id": msgRef.current.length + 1,
      "sender": {
        "name": name,
        "uid": uid,
        "avatar": avatar,
      },
    }
  }

  const submitMessage = (text, name, uid, avatar) => {
    requestClassification(text)
    requestGrammarExtraction(text)
    if (ws.current) {
      ws.current.send(text)
      let userMsg = createFullMessage(text, name, uid, avatar)
      updateMessages(userMsg)
    }
  }

  const updateMessages = msg => {
    setMessageHistory(currentMessages =>
      [...currentMessages, msg]
    )
  }

  const requestClassification = text => {
    postClassify(text).then(response => {
      if (response.status === 200) {
        let dataObj = JSON.parse(JSON.stringify(response.data.classifications))
        let newWordClassifications = wordClassifications.reverse().concat(dataObj)
        const filteredWordClassifications = removeDuplicates(newWordClassifications)
        setWordClassifications(filteredWordClassifications.reverse())
      }
    })
      .catch(error => {
        console.error(error)
      });
  }

  const requestGrammarExtraction = text => {
    postExtract(text).then(response => {
      if (response.status === 200) {
        let dataObj = JSON.parse(JSON.stringify(response.data.grammars))
        let newGrammarRules = grammarRules.reverse().concat(dataObj)
        const filteredGrammarRules = removeDuplicates(newGrammarRules)
        setGrammarRules(filteredGrammarRules.reverse())
      }
    })
      .catch(error => {
        console.error(error)
      });
  }

  return (
    <div className="chat-wrapper">
      <h1>中文聊天机器人</h1>
      <h1>(Chinese Chatbot)</h1>
      <div className='chat_items_container'>
        <div className="box">
          <h2>Grammar Breakdown</h2>
          <BootstrapTable
            classes='body-color'
            keyField='id'
            data={grammarRules}
            columns={columnsGrammar}
            pagination={paginationFactory({ hideSizePerPage: true, hidePageListOnlyOnePage: true })}
            noDataIndication="Send a message to see the level of grammar used"
          />
          <h4>Average Level: {averageGrammarLevel}</h4>
        </div>
        <div className="box">
          <ChatBox
            messages={messageHistory}
            onSubmit={(newMsg) => submitMessage(newMsg, 'currentUser', "user1", USER_AVATAR)}
            isLoading={loading}
            user={currnetUser} />
        </div>
        <div className="box">
          <h2>Word Breakdown</h2>
          <BootstrapTable
            classes='body-color'
            keyField='id'
            data={wordClassifications}
            columns={columnsWord}
            pagination={paginationFactory({ hideSizePerPage: true, hidePageListOnlyOnePage: true })}
            noDataIndication="Send a message to see the level of each word used" />
          <h4>Average Level: {averageWordLevel} </h4>
        </div>
      </div>

    </div>
  );
}

export default Chat;
