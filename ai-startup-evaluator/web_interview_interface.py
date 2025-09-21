#!/usr/bin/env python3
"""
Web interface for the ADK Interview Agent
Provides a simple web interface to interact with the interview agent
"""

import os
import sys
import json
from datetime import datetime
from flask import Flask, render_template, request, jsonify, session
import uuid

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.agents.adk_interview_agent import interview_agent

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Store active sessions in memory (in production, use Redis or database)
active_sessions = {}

@app.route('/')
def index():
    """Main page"""
    return render_template('interview_interface.html')

@app.route('/start_interview', methods=['POST'])
def start_interview():
    """Start a new interview session"""
    try:
        data = request.get_json()
        founder_name = data.get('founder_name', 'Anonymous')
        startup_name = data.get('startup_name', '')
        
        # Start interview session
        result = interview_agent.start_interview_session(founder_name, startup_name)
        
        if result['status'] == 'success':
            # Store session data
            session_id = result['session_id']
            active_sessions[session_id] = {
                'session_data': result['session_data'],
                'conversation_history': [],
                'start_time': datetime.now().isoformat()
            }
            
            return jsonify({
                'status': 'success',
                'session_id': session_id,
                'greeting': result['greeting'],
                'total_questions': result['total_questions']
            })
        else:
            return jsonify({
                'status': 'error',
                'message': result.get('error_message', 'Failed to start interview')
            })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        })

@app.route('/send_response', methods=['POST'])
def send_response():
    """Process founder's response"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        response = data.get('response', '')
        
        if not session_id or session_id not in active_sessions:
            return jsonify({
                'status': 'error',
                'message': 'Invalid session ID'
            })
        
        # Get session data
        session_data = active_sessions[session_id]['session_data']
        
        # Process response
        result = interview_agent.process_founder_response(session_data, response)
        
        if result['status'] == 'success':
            # Store conversation history
            active_sessions[session_id]['conversation_history'].append({
                'timestamp': datetime.now().isoformat(),
                'founder_response': response,
                'interviewer_response': result['next_message'],
                'analysis': result['analysis'],
                'progress': result['progress']
            })
            
            response_data = {
                'status': 'success',
                'interviewer_message': result['next_message'],
                'analysis': result['analysis'],
                'progress': result['progress'],
                'current_question': result.get('current_question', ''),
                'current_category': result.get('current_category', ''),
                'next_action': result.get('next_action', '')
            }
            
            # Check if interview is completed
            if result.get('interview_completed'):
                response_data['interview_completed'] = True
                response_data['summary_report'] = result.get('summary_report', {})
                response_data['gcs_path'] = result.get('gcs_path', '')
                response_data['completion_message'] = result.get('completion_message', '')
            
            return jsonify(response_data)
        else:
            return jsonify({
                'status': 'error',
                'message': result.get('error_message', 'Failed to process response')
            })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        })

@app.route('/get_session_status/<session_id>')
def get_session_status(session_id):
    """Get current session status"""
    try:
        if session_id not in active_sessions:
            return jsonify({
                'status': 'error',
                'message': 'Session not found'
            })
        
        session_data = active_sessions[session_id]
        
        return jsonify({
            'status': 'success',
            'session_id': session_id,
            'conversation_count': len(session_data['conversation_history']),
            'start_time': session_data['start_time'],
            'conversation_history': session_data['conversation_history']
        })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        })

@app.route('/end_session/<session_id>')
def end_session(session_id):
    """End interview session"""
    try:
        if session_id in active_sessions:
            del active_sessions[session_id]
            return jsonify({
                'status': 'success',
                'message': 'Session ended'
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Session not found'
            })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        })

if __name__ == '__main__':
    print("🌐 Starting ADK Interview Agent Web Interface")
    print("=" * 50)
    print("📱 Open your browser and go to: http://localhost:5000")
    print("=" * 50)
    
    app.run(debug=True, host='0.0.0.0', port=5000)