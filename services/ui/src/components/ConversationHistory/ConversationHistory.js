import 'react-bootstrap-table2-filter/dist/react-bootstrap-table2-filter.min.css';
import 'react-bootstrap-table2-paginator/dist/react-bootstrap-table2-paginator.min.css';
import './ConversationHistory.css'
import React, { useState, useEffect } from "react";
import { getConverstaionHistory } from '../../utils/api-client'
import paginationFactory from 'react-bootstrap-table2-paginator';
import filterFactory, { selectFilter } from 'react-bootstrap-table2-filter';
import BootstrapTable from 'react-bootstrap-table-next';
import { Tabs, Tab } from "react-bootstrap/";
import Pagination from '../Pagination/Pagination'
import Spinner from 'react-bootstrap-spinner';

const ConversationHistory = () => {
    const [historyState, setHistoryState] = useState({
        allConversations: [],
        currentConversation: [],
        currentPage: null,
        totalPages: null,
        averageWordLevel: 0,
        averageGrammarLevel: 0

    });
    const [fetchState, setFetchState] = useState('fetching');

    useEffect(() => {
        let isMounted = true;
        if (isMounted) {
            getConverstaionHistory().then(response => {
                if (response.status === 200) {
                    let dataObj = JSON.parse(JSON.stringify(response.data))
                    setHistoryState(prevState => {
                        return { ...prevState, allConversations: dataObj.conversations }
                    })
                }
                setFetchState('fetched')
            }).catch(error => {
                console.error(error)
            });
        }
        return () => { isMounted = false; };

    }, [])

    useEffect(() => {
        calcAverages(currentConversation[0])
    }, [historyState.currentConversation])

    const selectOptions = {
        1: '1',
        2: '2',
        3: '3',
        4: '4',
        5: '5',
        6: '6'
    };

    const columnsWord = [{
        dataField: 'word',
        text: 'Word'
    }, {
        dataField: 'level',
        text: 'Level' + '\xa0'.repeat(80) + `Average Level: ${historyState.averageWordLevel}`,
        sort: true,
        filter: selectFilter({
            options: selectOptions,
            className: 'filter',
            placeholder: 'Filter by level',
        })
    }];

    const columnsGrammar = [{
        dataField: 'pattern',
        text: 'Grammar Pattern'
    }, {
        dataField: 'level',
        text: 'Level' + '\xa0'.repeat(70) + `Average Level: ${historyState.averageGrammarLevel}`,
        sort: true,
        filter: selectFilter({
            options: selectOptions,
            className: 'filter',
            placeholder: 'Filter by level',
        })
    }];

    const calcAverage = (array) => {
        let sum = 0;
        if (array.length === 0) {
            return sum;
        }
        array.forEach(item => {
            sum += parseInt(item.level)
        })
        let average = sum / array.length
        return Math.round(average * 100) / 100;
    }

    const calcAverages = conversation => {
        if (conversation) {
            let wordsAverage = calcAverage(conversation.words)
            let grammarsAverage = calcAverage(conversation.grammars)
            setHistoryState(prevState => {
                return {
                    ...prevState,
                    averageWordLevel: wordsAverage,
                    averageGrammarLevel: grammarsAverage
                }
            })
        }
    }

    const onPageChanged = data => {
        const { allConversations } = historyState;
        const { currentPage, totalPages, pageLimit } = data;
        const offset = (currentPage - 1) * pageLimit;
        const currentConversation = allConversations.slice(offset, offset + pageLimit);
        setHistoryState(prevState => {
            return {
                ...prevState,
                currentPage: currentPage,
                currentConversation: currentConversation,
                totalPages: totalPages
            }
        })
    }

    const { allConversations, currentConversation, currentPage, totalPages } = historyState;
    const totalConversations = allConversations.length;
    let startTime
    let endTime
    let duration
    if (currentConversation.length > 0) {
        let startDate = new Date(currentConversation[0].start_time.replace(' ', 'T'));
        let endDate = new Date(currentConversation[0].end_time.replace(' ', 'T'));
        startTime = 'Start time: ' + startDate.toDateString() + ' ' + startDate.toLocaleTimeString();
        endTime = 'End time: ' + endDate.toDateString() + ' ' + endDate.toLocaleTimeString();
        let durationStatement = currentConversation[0].duration === 0 ? "less than 1 minute" : currentConversation[0].duration + " minutes"
        duration = 'Duration: ' + durationStatement
    }

    const getHistoryDisplay = () => {
        const headerClass = ['text-dark py-2 pr-4 m-0', currentPage ? 'border-gray border-right' : ''].join(' ').trim();
        return (<div className="row d-flex flex-row py-5">
            <div className="w-100 d-flex flex-row flex-wrap align-items-center justify-content-between">
                <div className="d-flex flex-row align-items-center">
                    <h2 className={headerClass}>
                        Total Conversations: <strong>{totalConversations}</strong>
                    </h2>

                    {currentPage && (
                        <span className="current-page d-inline-block h-100 pl-4 text-secondary">
                            Page <span className="font-weight-bold">{currentPage}</span> / <span className="font-weight-bold">{totalPages}</span>
                        </span>
                    )}

                </div>

                <div className="d-flex flex-row py-4 align-items-center">
                    <Pagination totalRecords={totalConversations} pageNeighbours={1} onPageChanged={onPageChanged} />
                </div>
            </div>
            {currentConversation.length > 0 ?
                < div className="w-100">
                    <h3 style={{ float: 'right' }}>{duration}</h3>
                    <h3>{startTime}</h3>
                    <h3>{endTime}</h3>
                    <Tabs defaultActiveKey="words">
                        <Tab eventKey="words" title="Words">
                            <BootstrapTable
                                classes='body-color'
                                keyField='id'
                                data={currentConversation[0].words}
                                columns={columnsWord}
                                pagination={paginationFactory({ hideSizePerPage: true, hidePageListOnlyOnePage: true })}
                                filter={filterFactory()}
                                noDataIndication="No words saved for this conversation" />
                        </Tab>
                        <Tab eventKey="grammar_patterns" title="Grammar Patterns">
                            <BootstrapTable
                                classes='body-color'
                                keyField='grammar_id'
                                data={currentConversation[0].grammars}
                                columns={columnsGrammar}
                                pagination={paginationFactory({ hideSizePerPage: true, hidePageListOnlyOnePage: true })}
                                filter={filterFactory()}
                                noDataIndication="No grammar patterns saved for this conversation" />
                        </Tab>
                    </Tabs>
                </div> : null}
        </div>);
    }

    if (fetchState === 'fetching') {
        return (
          <div className='home'>
            <Spinner type="border" color="primary" size="20" />
          </div>
        )
      }

    return (
        <div className="conversationHistoryContainer">
            <h1 className='title'>
                <strong>Conversation History</strong>
            </h1>
            {totalConversations > 0 ? getHistoryDisplay() : <h3 className='center'> You have no conversations saved. Why don't you go and have a conversation with the chinese chatbot</h3>}
        </div >
    );
}

export default ConversationHistory;